from sqlmodel import select, and_
from uuid import UUID
from app.models.permission import Permission
from app.schemas.permission import IPermissionCreate, IPermissionUpdate
from app.crud.base_sqlmodel import CRUDBase
from sqlmodel.ext.asyncio.session import AsyncSession


class CRUDPermission(CRUDBase[Permission, IPermissionCreate, IPermissionUpdate]):

    async def get_permission_by_resource_id_role_id(self, db_session: AsyncSession, *, permission: Permission) -> Permission:
        permission = await db_session.exec(select(Permission).where(and_(Permission.resource_id == permission.resource_id, Permission.role_id == permission.role_id)))
        return permission.first()

    async def get_permission_by_resource_id(self, db_session: AsyncSession, *, resource_id: UUID) -> Permission:
        permission = await db_session.exec(select(Permission).where(Permission.resource_id == resource_id))
        return permission.first()


permission = CRUDPermission(Permission)
