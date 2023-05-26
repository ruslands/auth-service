# # Native # #
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from uuid import UUID

# # Installed # #
from sqlalchemy.orm import selectinload
from pydantic.networks import EmailStr
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import SQLAlchemyError

# # Package # #
from core.base.crud import CRUDBase
from app.user.schema import ICreate, IUpdate
from core.exceptions import BadRequestException, ConflictException
from core.security import verify_password
from app.user.model import User
from app.role.model import Role
from app.team.model import Team
from app.visibility_group.model import Visibility_Group

__all__ = ("user",)


class CRUD(CRUDBase[User, ICreate, IUpdate]):
    async def get_by_email(
        self, db_session: AsyncSession, *, email: str
    ) -> Optional[User]:
        users = await db_session.exec(
            select(User).where(User.email == email).options(selectinload("*"))
        )
        return users.first()

    async def update_role(
        self, db_session: AsyncSession, *, id: UUID, role: Role
    ) -> None:
        user = await super().get(db_session, id=id)
        if role in user.roles:
            user.roles.remove(role)
        else:
            user.roles.append(role)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return

    async def update_team(
        self, db_session: AsyncSession, *, id: UUID, team: Team
    ) -> None:
        user = await super().get(db_session, id=id)
        if team in user.teams:
            user.teams.remove(team)
        else:
            user.teams.append(team)
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return

    async def update_visibility_group(
        self, db_session: AsyncSession, *, id: UUID, visibility_group: Visibility_Group
    ) -> None:
        user = await super().get(db_session, id=id)
        if visibility_group == user.visibility_group:
            user.visibility_group = None
        else:
            user.visibility_group = visibility_group
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return

    async def update_is_active(
        self,
        db_session: AsyncSession,
        *,
        db_obj: List[User],
        obj_in: Union[int, str, Dict[str, Any]],
    ) -> Union[User, None]:
        response = None
        for x in db_obj:
            setattr(x, "is_active", obj_in.is_active)
            setattr(x, "updated_at", datetime.utcnow())
            db_session.add(x)
            await db_session.commit()
            await db_session.refresh(x)
            response.append(x)
        return response

    async def authenticate(
        self, db_session: AsyncSession, *, email: EmailStr, password: str
    ) -> Optional[User]:
        try:
            user = await self.get_by_email(db_session, email=email)
        except SQLAlchemyError as e:
            raise ConflictException(detail=f"Database error: {e.orig}")
        if not user:
            raise BadRequestException(detail="Incorrect email or password")
        if not user.is_active:
            raise ConflictException(detail="User is disabled")
        if not user.allow_basic_login:
            raise ConflictException(detail="Basic login is disabled for this user")
        if not await verify_password(password, user.hashed_password):
            raise BadRequestException(detail="Incorrect email or password")
        return user


user = CRUD(User)
