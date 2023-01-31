# # Native # #
from uuid import UUID

# # Installed # #

# # Package # #
from app.models.permission import PermissionBase
from app.models.base_uuid_model import BaseUUIDModel


__all__ = (
    "ICreate",
    "IRead",
    "IUpdate",
)


class ICreate(PermissionBase):
    ...


class IRead(PermissionBase, BaseUUIDModel):
    ...


class IUpdate(PermissionBase):
    ...
