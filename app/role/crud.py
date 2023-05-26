# # Native # #

# # Installed # #
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

# # Package # #
from app.role.schema import ICreate, IUpdate
from app.role.model import Role
from core.base.crud import CRUDBase


class CRUD(CRUDBase[Role, ICreate, IUpdate]):
    async def get_role_by_title(self, db_session: AsyncSession, *, title: str) -> Role:
        role = await db_session.exec(select(Role).where(Role.title == title))
        return role.first()


role = CRUD(Role)
