# # Native # #
from uuid import UUID
from typing import Optional, List

# # Installed # #

# # Package # #
from app.models.role import RoleBase
from app.schemas.resource import IRead as ResourceRead
from app.models.base_uuid_model import BaseUUIDModel


class ICreate(RoleBase):
    ...


class IRead(RoleBase, BaseUUIDModel):
    resources: Optional[List[ResourceRead]]


class IUpdate(RoleBase, BaseUUIDModel):
    ...
