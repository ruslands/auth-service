# # Native # #

# # Installed # #

# # Package # #
from app.permission.model import PermissionBase
from core.base.model import BaseUUIDModel


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


class IFilter(PermissionBase):
    ...
