
# # Native # #
from typing import Optional, Callable, Awaitable

# # Installed # #
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
# from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel.ext.asyncio.session import AsyncSession

# # Package # #
from core.settings import settings
from core.security import verify_jwt_token
from app.user.model import User
from app import crud
from core.exceptions import NotFoundException, UnauthorizedException, ConflictException, ForbiddenException
from core.base.schema import IMetaGeneral
from app.rbac.schema import IRBACValidate
from core.database.session import get_session

__all__ = (
    "get_general_meta",
    "get_current_user"
)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.HOSTNAME}/api/auth/access-token"
)


async def get_general_meta(
    db_session: AsyncSession = Depends(get_session)
) -> IMetaGeneral:
    current_roles = await crud.role.get_multi(db_session, skip=0, limit=100)
    return IMetaGeneral(roles=current_roles)


def get_current_user(
    required_permissions: Optional[bool] = None
) -> Callable[[Request, AsyncSession, str], Awaitable[User]]:
    async def current_user(
            request: Request,
            db_session: AsyncSession = Depends(get_session),
            access_token: str = Depends(reusable_oauth2)
    ) -> User:
        payload = await verify_jwt_token(token=access_token, token_type="access", db_session=db_session, crud=crud)

        user = await crud.user.get(db_session, id=payload["user_id"])
        if not user:
            raise NotFoundException(detail="User not found")
        if not user.sessions:
            raise UnauthorizedException(detail="User has no active sessions")
        if not user.is_active:
            raise ConflictException(detail="User is not active")
        if required_permissions:
            data = await request.app.rbac.validate(
                db_session,
                IRBACValidate.parse_obj({
                    "endpoint": str(request.url),
                    "method": request.method}),
                access_token=access_token)
            if not data['access']:
                raise ForbiddenException(detail="User does not have required permissions")
            # TODO validate visibility
        return user

    return current_user
