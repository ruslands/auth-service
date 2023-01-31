# # Native # #
from uuid import UUID

# # Installed # #

# # Package # #
from app.models.permission import PermissionBase


__all__ = (
    "ICreate",
    "IRead",
    "IUpdate",
)


class ICreate(PermissionBase):
    role_id: UUID
    resource_id: UUID


class IRead(PermissionBase):
    role_id: UUID
    resource_id: UUID


class IUpdate(PermissionBase):
    pass
