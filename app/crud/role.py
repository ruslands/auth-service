# # Native # #

# # Installed # #
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

# # Package # #
from app.schemas.role import ICreate, IUpdate
from app.models.role import Role
from app.crud.base_sqlmodel import CRUDBase


class CRUD(CRUDBase[Role, ICreate, IUpdate]):
    async def get_role_by_name(self, db_session: AsyncSession, *, name: str) -> Role:
        role = await db_session.exec(select(Role).where(Role.name == name))
        return role.first()


role = CRUD(Role)
