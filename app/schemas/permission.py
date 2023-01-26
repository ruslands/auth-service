# # Native # #
from uuid import UUID

# # Installed # #

# # Package # #
from app.models.permission import PermissionBase


__all__ = (
    "IPermissionCreate",
    "IPermissionRead",
    "IPermissionUpdate",
)


class IPermissionCreate(PermissionBase):
    role_id: UUID
    resource_id: UUID


class IPermissionRead(PermissionBase):
    role_id: UUID
    resource_id: UUID


class IPermissionUpdate(PermissionBase):
    pass
