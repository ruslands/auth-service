import uuid
from typing import Optional

from pydantic import BaseModel


class RoleCacheSchema(BaseModel):
    id: uuid.UUID
    title: str

    class Config:
        orm_mode = True


class ResourceCacheSchema(BaseModel):
    id: uuid.UUID
    endpoint: str
    method: str
    is_rbac_enabled: Optional[bool]
    is_visibility_group_enabled: Optional[bool]

    class Config:
        orm_mode = True


class PermissionCacheSchema(BaseModel):
    id: uuid.UUID
    role_id: uuid.UUID
    resource_id: uuid.UUID

    class Config:
        orm_mode = True


class RoleListCacheSchema(BaseModel):
    __root__: list[RoleCacheSchema]


class ResourceListCacheSchema(BaseModel):
    __root__: list[ResourceCacheSchema]


class PermissionListCacheSchema(BaseModel):
    __root__: list[PermissionCacheSchema]
