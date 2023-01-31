# # Native # #
from uuid import UUID
from typing import Optional, List

# # Installed # #

# # Package # #
from app.models.role import RoleBase
from app.schemas.resource import IRead
from app.models.base_uuid_model import BaseUUIDModel


class ICreate(RoleBase):
    pass


class IRead(RoleBase):
    id: UUID


class IReadWithPermissions(RoleBase):
    id: UUID
    resources: Optional[List["IRead"]]


class IUpdate(RoleBase, BaseUUIDModel):
    pass
