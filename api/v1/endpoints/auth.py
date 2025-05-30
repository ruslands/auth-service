# # Native # #
import os
from datetime import timedelta
from enum import Enum
from typing import Any, Optional, Tuple
from urllib.parse import urlparse, parse_qs

# # Installed # #
from fastapi import APIRouter, Body, Depends, Request, Header, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi_sso.sso.base import SSOBase
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.facebook import FacebookSSO
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic.networks import AnyHttpUrl

# # Package # #
from core.database.session import get_session
from core.security import create_jwt_token, verify_jwt_token, create_cookie
from core.settings import settings
from core.logger import logger
from core.exceptions import ConflictException, NotFoundException, UnauthorizedException, BadRequestException
from core.constants import AMOUNT_OF_SESSSIONS_PER_USER
from core.base.schema import IPostResponseBase, IGetResponseBase
from app.model import User
from app.user.util import get_current_user
from app.user.schema import ICreate, IIdentityProvider, IAuthMeta
from app.token.schema import Token, RefreshToken
from app.sessions.model import Sessions
from app import crud
from core.sso_providers import get_user_info_from_sso_provider, KeycloakSSO

router = APIRouter()

google_sso = GoogleSSO(
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    allow_insecure_http=True,
    use_state=False,
)

keycloak_sso = KeycloakSSO(
    client_id=settings.KEYCLOAK_CLIENT_ID,
    client_secret=settings.KEYCLOAK_CLIENT_SECRET,
    allow_insecure_http=True,
    use_state=False,
)

facebook_sso = FacebookSSO(
    client_id=settings.FACEBOOK_CLIENT_ID,
    client_secret=settings.FACEBOOK_CLIENT_SECRET,
    allow_insecure_http=True,
    use_state=False,
)

if any((google_sso.allow_insecure_http, keycloak_sso.allow_insecure_http, facebook_sso.allow_insecure_http)):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.HOSTNAME}/api/auth/access-token"
)


class SSOProvider(str, Enum):
    keycloak = "keycloak"
    google = "google"
    facebook = "facebook"


def get_sso_provider(provider: SSOProvider) -> SSOBase:
    match provider:
        case SSOProvider.google:
            return google_sso
        case SSOProvider.keycloak:
            return keycloak_sso
        case SSOProvider.facebook:
            return facebook_sso
        case _:
            raise NotFoundException(detail="Provider not found")


def create_token_and_session(
    user,
    request: Request,
    response: Response) -> Tuple[Token, Sessions, IAuthMeta]:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token, expires_at = create_jwt_token({
        "user_id": str(user.id),
        "email": user.email,
        "roles": {str(i.id): i.title for i in user.roles},
        "teams": [str(i.id) for i in user.teams],
        "visibility_group": user.visibility_group.prefix if user.visibility_group else None
    }, expires_delta=access_token_expires, token_type="access")

    refresh_token, _ = create_jwt_token({
        "user_id": str(user.id)
    }, expires_delta=refresh_token_expires, token_type="refresh")

    cookie = request.cookies.get("auth")
    if not cookie:
        cookie = create_cookie()
        response.set_cookie(key="auth", value=cookie, httponly=True, secure=True)

    data = Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        expires_at=expires_at,
        cookie=cookie
    )

    session = Sessions(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        expires_at=expires_at,
        cookie=cookie
    )

    meta = IAuthMeta.parse_obj(user)

    return data, session, meta


async def refresh_user_sessions(user: User, request: Request, db_session: AsyncSession, session: Sessions):
    if user.sessions:
        for i in user.sessions:
            if i.cookie == request.cookies.get("auth"):
                await crud.sessions.remove(db_session, id=i.id)
        if len(user.sessions) >= AMOUNT_OF_SESSSIONS_PER_USER:
            oldest_session = sorted(
                user.sessions, key=lambda x: x.created_at)[0]
            await crud.sessions.remove(db_session, id=oldest_session.id)
    await crud.sessions.create(db_session, obj_in=session)


@router.post("/auth/basic", response_model=IPostResponseBase[Token], status_code=201,
             responses={
    409: {
        "content": {"application/json": {"example": {"detail": "User is disabled"}}},
        "description": "Additional information about the error",
    }
})
async def basic(
    response: Response,
    request: Request,
    db_session: AsyncSession = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
    # meta_data: IMetaGeneral = Depends(get_general_meta) # TODO return available roles
) -> Any:
    """
    Basic login for test users only. Disabled for rest of the users.
    """
    user = await crud.user.authenticate(db_session, email=form_data.username, password=form_data.password)
    data, session, meta = create_token_and_session(user, request, response)
    await refresh_user_sessions(user, request, db_session, session)
    return IPostResponseBase[Token](meta=meta, data=data, message="Login correctly")


@router.get("/auth/logout", response_model=IGetResponseBase, responses={
    401: {
        "content": {"application/json": {"example": {"detail": "The session does not exist"}}},
        "description": "If user can't be authenticated",
    },
    403: {
        "content": {"application/json": {"example": {"detail": "User does not have permission"}}},
        "description": "If user authenticated but not authorized",
    },
    404: {
        "content": {"application/json": {"example": {"detail": "Not found"}}},
        "description": "Not found",
    },
    409: {
        "content": {"application/json": {"example": {"detail": "Conflict"}}},
        "description": "Conflict",
    }
})
async def logout(
    request: Request,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user()),
    access_token: str = Depends(reusable_oauth2)
):
    if current_user.sessions:
        for i in current_user.sessions:
            if i.cookie == request.cookies.get("auth") or i.access_token == access_token:
                await crud.sessions.remove(db_session, id=i.id)
    return IGetResponseBase(data={})

@router.get("/auth/{provider}", status_code=303)
async def auth_provider(
    provider: SSOProvider,
    request: Request,
    redirect_uri: Optional[AnyHttpUrl] = False,
    redirect_enable: Optional[bool] = True,
    state: Optional[str] = None,
    sso_provider: SSOBase = Depends(get_sso_provider),
) -> Any:
    """Generate login url or redirect"""
    sso_provider.state = state
    if not redirect_uri:
        redirect_uri = request.url_for(
            "auth_callback", provider=provider.value)
    if not redirect_enable:
        return await sso_provider.get_login_url(redirect_uri=redirect_uri)
    return await sso_provider.get_login_redirect(redirect_uri=redirect_uri)


@router.get("/auth/{provider}/callback", response_model=IGetResponseBase[Token], status_code=200, responses={
    400: {
        "content": {"application/json": {"example": {"detail": "Bad request"}}},
        "description": "Bad request",
    },
    404: {
        "content": {"application/json": {"example": {"detail": "Not found"}}},
        "description": "Not found",
    },
    409: {
        "content": {"application/json": {"example": {"detail": "Conflict"}}},
        "description": "Conflict",
    }
})
async def auth_callback(
    provider: SSOProvider,
    request: Request,
    response: Response,
    db_session: AsyncSession = Depends(get_session),
    redirect_uri: Optional[AnyHttpUrl] = Header(
        default=None, convert_underscores=True),
    sso_provider: SSOBase = Depends(get_sso_provider)
) -> Any:
    """Process login response from sso provider and return user info"""
    #####################################################
    logger.debug(f"before: {request.url}")
    # extract state
    parsed_request_uri = urlparse(str(request.url))
    state = parse_qs(parsed_request_uri.query).get("state", [None])[0]
    # update redirect uri
    logger.debug(f"redirect_uri: {redirect_uri}")
    if not redirect_uri:
        redirect_uri = request.url_for(
            "auth_callback", provider=provider.value)
    parsed_redirect_uri = urlparse(redirect_uri)
    request._url = request._url.replace(
        scheme=parsed_redirect_uri.scheme,
        netloc=parsed_redirect_uri.netloc,
        path=parsed_redirect_uri.path
    )
    for i in request.__dict__['scope']['headers']:
        if i[0] == b'host':
            request.__dict__['scope']['headers'].remove(i)
            break
    request.__dict__['scope']['headers'] += [
        (b'host', parsed_redirect_uri.netloc.replace("https://", "").replace("http://", "").encode())]
    logger.debug(f"after: {request.url}")
    #####################################################
    try:
        # id, picture, email, display_name, provider
        sso_user = await sso_provider.verify_and_process(request)
        logger.debug(f"{provider.value} user: {sso_user}")
    except Exception as e:
        raise BadRequestException(detail=str(e))
    try:
        user = await crud.user.get_by_email(db_session, email=sso_user.email)
    except Exception as e:
        raise ConflictException(detail=f"database error: {e}")
    if not user:
        new_user = ICreate.parse_obj(sso_user.dict())
        logger.debug(f"user not found, creating new user: {new_user}")
        user = await crud.user.create(db_session, obj_in=new_user)
        logger.debug(f"new user created: {user}")
        user = await crud.user.get(db_session, id=user.id)
        # raise ConflictException(detail="User not found")
    elif not user.is_active:
        raise ConflictException(detail="user is disabled")

    data, session, meta = create_token_and_session(user, request, response)
    await refresh_user_sessions(user, request, db_session, session)

    return IGetResponseBase[Token](meta=meta, data=data, message="Login correctly")


@router.post("/auth/refresh-token", response_model=IPostResponseBase[Token],
             response_model_exclude_none=True, status_code=201, responses={
    401: {
        "content": {"application/json": {"example": {"detail": "The session does not exist"}}},
        "description": "If user can't be authenticated",
    },
    404: {
        "content": {"application/json": {"example": {"detail": "Not found"}}},
        "description": "Not found",
    },
    409: {
        "content": {"application/json": {"example": {"detail": "Conflict"}}},
        "description": "Conflict",
    }
})
async def refresh_token(
    request: Request,
    response: Response,
    body: RefreshToken = Body(...),
    db_session: AsyncSession = Depends(get_session),
) -> Any:
    """
    Get Refresh token
    """
    payload = await verify_jwt_token(token=body.refresh_token, token_type="refresh", db_session=db_session, crud=crud)
    try:
        user = await crud.user.get(db_session, id=payload['user_id'])
    except Exception as e:
        raise ConflictException(detail=f"database error: {e}")
    if not user:
        raise NotFoundException(detail="User not found")
    elif not user.is_active:
        raise ConflictException(detail="User is disabled")
    if not user.sessions:
        raise UnauthorizedException(detail="The session does not exist")
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token, expires_at = create_jwt_token({
        "user_id": str(user.id),
        "email": user.email,
        "roles": {str(i.id): i.title for i in user.roles},
        "teams": [str(i.id) for i in user.teams],
        "visibility_group": user.visibility_group.prefix if user.visibility_group else None
    }, expires_delta=access_token_expires, token_type="access")
    data = Token(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at,
        refresh_token=body.refresh_token
    )
    meta = IAuthMeta.parse_obj(user)
    cookie = request.cookies.get("auth")
    for s in user.sessions:
        if s.refresh_token == body.refresh_token:
            if not cookie:
                if s.cookie:
                    cookie = s.cookie
                    response.set_cookie(
                        key="auth", value=cookie, httponly=True, secure=True)
                else:
                    cookie = create_cookie()
                    response.set_cookie(
                        key="auth", value=cookie, httponly=True, secure=True)
            await crud.sessions.update(db_session, obj_current=s, obj_new={
                "access_token": access_token,
                "expires_at": expires_at,
                cookie: cookie
            })
            return IPostResponseBase[Token](meta=meta, data=data, message="Access token generated correctly")
    raise UnauthorizedException(detail="The session does not exist")


@router.post("/auth/identity-provider", response_model=IPostResponseBase[Token], status_code=200)
async def idp(
    data: IIdentityProvider,
    request: Request,
    response: Response,
    db_session: AsyncSession = Depends(get_session),
):
    # Get SSO provider
    sso_provider = get_sso_provider(SSOProvider(data.idp))
    # Retrieve user data from SSO provider
    user_data = await get_user_info_from_sso_provider(sso_provider, data.idp_access_token)
    logger.debug(f"user data: {user_data}")
    user_data = ICreate.parse_obj(user_data)
    try:
        user = await crud.user.get_by_email(db_session, email=user_data.email)
    except Exception as e:
        raise ConflictException(detail=f"database error: {e.orig}")
    if not user:
        new_user = ICreate.parse_obj(user_data.dict())
        logger.debug(f"user not found, creating new user: {new_user}")
        user = await crud.user.create(db_session, obj_in=new_user)
        user = await crud.user.get_by_email(db_session, email=user.email)
    elif not user.is_active:
        raise ConflictException(detail="user is disabled")

    data, session, meta = create_token_and_session(user, request, response)
    await refresh_user_sessions(user, request, db_session, session)

    return IGetResponseBase[Token](meta=meta, data=data, message="Login correctly")
