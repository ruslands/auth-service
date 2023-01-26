# # Native # #

# # Installed # #
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

# # Package # #
from app.schemas.role import IRoleCreate, IRoleUpdate
from app.models.role import Role
from app.crud.base_sqlmodel import CRUDBase


class CRUDRole(CRUDBase[Role, IRoleCreate, IRoleUpdate]):
    async def get_role_by_name(self, db_session: AsyncSession, *, name: str) -> Role:
        role = await db_session.exec(select(Role).where(Role.name == name))
        return role.first()


role = CRUDRole(Role)
