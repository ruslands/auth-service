# # Native # #
from uuid import UUID
from typing import Optional, List

# # Installed # #

# # Package # #
from app.role.model import RoleBase
from app.resource.schema import IRead as ResourceRead
from core.base.model import BaseUUIDModel


class ICreate(RoleBase):
    ...


class IRead(RoleBase, BaseUUIDModel):
    resources: Optional[List[ResourceRead]]


class IUpdate(RoleBase, BaseUUIDModel):
    ...
