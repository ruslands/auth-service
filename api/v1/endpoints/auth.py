# # Native # #
import hashlib
import os
from datetime import timedelta
from typing import Any, Optional
from urllib.parse import urlparse, parse_qs

# # Installed # #
from fastapi import APIRouter, Body, Depends, Request, Header, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi_sso.sso.google import GoogleSSO
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic.networks import AnyHttpUrl
from sqlalchemy.exc import SQLAlchemyError

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
from app.user.schema import ICreate
from app.token.schema import Token, RefreshToken
from app.sessions.model import Sessions
from app import crud


router = APIRouter()

google_sso = GoogleSSO(
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    allow_insecure_http=True,
    use_state=False,
)
if google_sso.allow_insecure_http:
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.HOSTNAME}/api/auth/access-token"
)


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
    if not user.is_active:
        raise ConflictException(detail="User is disabled")
    if not user.allow_basic_login:
        raise ConflictException(detail="Basic login is disabled for this user")

    roles = {str(i.id): i.name for i in user.roles}
    teams = [str(i.id) for i in user.teams]

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token, expires_at = create_jwt_token({
        "user_id": str(user.id),
        "email": user.email,
        "roles": roles,
        "teams": teams,
        "visibility_group": user.visibility_group.prefix if user.visibility_group else None
    }, expires_delta=access_token_expires, type="access")
    refresh_token, _ = create_jwt_token({
        "user_id": str(user.id)
    }, expires_delta=refresh_token_expires, type="refresh")

    cookie = request.cookies.get("auth")
    if not cookie:
        cookie = create_cookie()
        response.set_cookie(key="auth", value=cookie, httponly=True, secure=True)

    data = Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        refresh_token_timeout=settings.REFRESH_TOKEN_TIMEOUT_MINUTES * 60,
        expires_at=expires_at,
        cookie=cookie
    )
    new_session = Sessions(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        expires_at=expires_at,
        cookie=cookie
    )
    meta = {
        "id": str(user.id),
        "full_name": user.full_name,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "roles": [i.name for i in user.roles],
        "picture": user.picture
    }
    if user.sessions:
        for i in user.sessions:
            if i.cookie == cookie:
                await crud.sessions.remove(db_session, id=i.id)
        if len(user.sessions) >= AMOUNT_OF_SESSSIONS_PER_USER:
            oldest_session = sorted(user.sessions, key=lambda x: x.created_at)[0]
            await crud.sessions.remove(db_session, id=oldest_session.id)
    await crud.sessions.create(db_session, obj_in=new_session)
    return IPostResponseBase[Token](meta=meta, data=data, message="Login correctly")


@router.get("/auth/google", status_code=303)
async def google(
    request: Request,
    redirect_uri: Optional[AnyHttpUrl] = False,
    redirect_enable: Optional[bool] = True,
    state: Optional[str] = None,
) -> Any:
    """Generate login url or redirect"""
    google_sso.state = state
    if not redirect_uri:
        redirect_uri = request.url_for("google_callback")
    if not redirect_enable:
        return await google_sso.get_login_url(redirect_uri=redirect_uri)
    return await google_sso.get_login_redirect(redirect_uri=redirect_uri)


@router.get("/auth/google/callback", response_model=IGetResponseBase[Token], status_code=200, responses={
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
async def google_callback(
    request: Request,
    response: Response,
    db_session: AsyncSession = Depends(get_session),
    redirect_uri: Optional[AnyHttpUrl] = Header(default=None, convert_underscores=True),
    # meta_data: IMetaGeneral = Depends(get_general_meta), # TODO return available roles
) -> Any:
    """Process login response from Google and return user info"""
    #####################################################
    logger.debug(f"before: {request.url}")
    # extract state
    parsed_request_uri = urlparse(str(request.url))
    state = parse_qs(parsed_request_uri.query).get("state", [None])[0]
    # update redirect uri
    logger.debug(f"redirect_uri: {redirect_uri}")
    if not redirect_uri:
        redirect_uri = request.url_for("google_callback")
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
        google_user = await google_sso.verify_and_process(request)
        logger.debug(f"google user: {google_user}")
    except Exception as e:
        raise BadRequestException(detail=str(e))
    try:
        user = await crud.user.get_by_email(db_session, email=google_user.email)
    except Exception as e:
        raise ConflictException(detail=f"database error: {e.orig}")
    if not user:
        new_user = ICreate.parse_obj(google_user.dict())
        logger.debug(f"user not found, creating new user: {new_user}")
        user = await crud.user.create(db_session, obj_in=new_user)
        user = await crud.user.get_by_email(db_session, email=user.email)
        # raise ConflictException(detail="User not found")
    elif not user.is_active:
        raise ConflictException(detail="user is disabled")

    roles = {str(i.id): i.name for i in user.roles}
    teams = [str(i.id) for i in user.teams]


    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token, expires_at = create_jwt_token({
        "user_id": str(user.id),
        "email": user.email,
        "roles": roles,
        "teams": teams,
        "visibility_group": user.visibility_group.prefix if user.visibility_group else None
    }, expires_delta=access_token_expires, type="access")
    refresh_token, _ = create_jwt_token({
        "user_id": str(user.id)
    }, expires_delta=refresh_token_expires, type="refresh")

    cookie = request.cookies.get("auth")
    if not cookie:
        cookie = create_cookie()
        response.set_cookie(key="auth", value=cookie, httponly=True, secure=True)

    data = Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        refresh_token_timeout=settings.REFRESH_TOKEN_TIMEOUT_MINUTES * 60,
        expires_at=expires_at,
        cookie=cookie,
    )
    new_session = Sessions(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.id,
        expires_at=expires_at,
        cookie=cookie,
    )
    meta = {
        "id": str(user.id),
        "full_name": user.full_name,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "roles": [i.name for i in user.roles],
        "picture": user.picture
    }
    if user.sessions:
        for i in user.sessions:
            if i.cookie == request.cookies.get("auth"):
                await crud.sessions.remove(db_session, id=i.id)
        if len(user.sessions) >= AMOUNT_OF_SESSSIONS_PER_USER:
            oldest_session = sorted(user.sessions, key=lambda x: x.created_at)[0]
            await crud.sessions.remove(db_session, id=oldest_session.id)
    await crud.sessions.create(db_session, obj_in=new_session)
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
    payload = await verify_jwt_token(token=body.refresh_token, type="refresh", db_session=db_session)
    try:
        user = await crud.user.get(db_session, id=payload['user_id'])
    except Exception as e:
        raise ConflictException(detail=f"database error: {e.orig}")
    if not user:
        raise NotFoundException(detail="User not found")
    elif not user.is_active:
        raise ConflictException(detail="User is disabled")
    if not user.sessions:
        raise UnauthorizedException(detail="The session does not exist")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    roles = {str(i.id): i.name for i in user.roles}
    teams = [str(i.id) for i in user.teams]
    access_token, expires_at = create_jwt_token({
        "user_id": str(user.id),
        "email": user.email,
        "roles": roles,
        "teams": teams,
        "visibility_group": user.visibility_group.prefix if user.visibility_group else None
    }, expires_delta=access_token_expires, type="access")
    data = Token(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at,
        refresh_token_timeout=settings.REFRESH_TOKEN_TIMEOUT_MINUTES * 60,
        refresh_token=body.refresh_token
    )
    meta = {
        "id": str(user.id),
        "full_name": user.full_name,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "roles": [i.name for i in user.roles],
        "picture": user.picture
    }
    cookie = request.cookies.get("auth")
    for s in user.sessions:
        if s.refresh_token == body.refresh_token:
            if not cookie:
                if s.cookie:
                    cookie = s.cookie
                    response.set_cookie(key="auth", value=cookie, httponly=True, secure=True)
                else:
                    cookie = create_cookie()
                    response.set_cookie(key="auth", value=cookie, httponly=True, secure=True)
            await crud.sessions.update(db_session, obj_current=s, obj_new={
                "access_token": access_token,
                "expires_at": expires_at,
                cookie: cookie
            })
            return IPostResponseBase[Token](meta=meta, data=data, message="Access token generated correctly")
    raise UnauthorizedException(detail="The session does not exist")


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
