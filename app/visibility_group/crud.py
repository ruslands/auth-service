# # Native # #

# # Installed # #
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload

# # Package # #
from app.visibility_group.schema import ICreate, IUpdate
from core.base.crud import CRUDBase
from app.visibility_group.model import Visibility_Group


class CRUD(CRUDBase[Visibility_Group, ICreate, IUpdate]):
    async def get_visibility_group_by_prefix(self, db_session: AsyncSession, *, prefix: str) -> Visibility_Group:
        visibility_group = await db_session.exec(select(Visibility_Group).where(Visibility_Group.prefix == prefix))
        return visibility_group.first()

    async def get_visibility_group_and_users(self, db_session: AsyncSession) -> Visibility_Group:
        visibility_group = await db_session.exec(select(Visibility_Group).options(selectinload(Visibility_Group.user)))
        return visibility_group.all()


visibility_group = CRUD(Visibility_Group)
