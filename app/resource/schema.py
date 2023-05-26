# # Native # #
from typing import Optional

# # Installed # #
from pydantic import BaseModel, validator

# # Package # #
from app.resource.model import ResourceBase
from core.base.model import BaseUUIDModel
from core.constants import VISIBILITY_GROUP_ENTITY_POSSIBLE_VALUES

__all__ = ("ICreate", "IRead", "IUpdate")


class ICreate(BaseModel):
    endpoint: str
    method: str
    description: Optional[str]
    rbac_enable: Optional[bool]
    visibility_group_enable: Optional[bool]
    visibility_group_entity: Optional[str]

    @validator("method", "endpoint")
    def method_must_be_lower(cls, v):
        return v.lower().strip()

    @validator("visibility_group_entity")
    def visibility_group_entity_possible_values(cls, v):
        if not v:
            return v
        if v not in VISIBILITY_GROUP_ENTITY_POSSIBLE_VALUES:
            raise ValueError(
                f"Invalid value: {v}. Possible values: {VISIBILITY_GROUP_ENTITY_POSSIBLE_VALUES}"
            )
        return v


class IRead(ResourceBase, BaseUUIDModel):
    ...


class IUpdate(ResourceBase):
    endpoint: Optional[str]
    method: Optional[str]
    description: Optional[str]
    rbac_enable: Optional[bool]
    visibility_group_enable: Optional[bool]
    visibility_group_entity: Optional[str]

    @validator("method", "endpoint")
    def method_must_be_lower(cls, v):
        if not v:
            return v
        return v.lower().strip()

    @validator("visibility_group_entity")
    def visibility_group_entity_possible_values(cls, v):
        if not v:
            return v
        possible_values = ["opportunity"]
        if v not in possible_values:
            raise ValueError(f"Invalid value: {v}. Possible values: {possible_values}")
        return v


class IFilter(ResourceBase):
    ...
