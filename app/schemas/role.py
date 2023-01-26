# # Native # #
from uuid import UUID
from typing import Optional, List

# # Installed # #

# # Package # #
from app.models.role import RoleBase
from app.schemas.resource import IResourceRead
from app.models.base_uuid_model import BaseUUIDModel


class IRoleCreate(RoleBase):
    pass


class IRoleRead(RoleBase):
    id: UUID


class IRoleReadWithPermissions(RoleBase):
    id: UUID
    resources: Optional[List["IResourceRead"]]


class IRoleUpdate(RoleBase, BaseUUIDModel):
    pass
