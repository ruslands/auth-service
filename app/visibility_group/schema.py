# # Native # #
from typing_extensions import TypedDict
from typing import Optional, List, Union
from uuid import UUID

# # Installed # #
from pydantic import BaseModel, validator

# # Package # #
from app.visibility_group.model import VisibilityGroupBase
from core.base.model import BaseUUIDModel
from core.constants import VISIBILITY_GROUP_ENTITY_SETTINGS

__all__ = (
    "ICreate",
    "IRead",
    "IUpdate",
    "IVisibilityGroupSettings",
    "IVisibilityGroupValidateResponse"
)


class IRead(VisibilityGroupBase, BaseUUIDModel):
    ...


class ICreate(BaseModel):
    prefix: str
    admin: Optional[UUID]
    opportunity: Optional[List[str]] = []
    seller: Optional[List[str]] = []
    activity: Optional[List[str]] = []
    property: Optional[List[str]] = []

    @validator('prefix')
    def prefix_attr_normalization(cls, v):
        return v.lower().strip().strip('/')

    @validator('opportunity', 'seller', 'activity', 'property')
    def visibility_group_entity_validation(cls, v):
        v = list(map(lambda x: x.lower().strip(), v))
        for value in v:
            if value not in VISIBILITY_GROUP_ENTITY_SETTINGS:
                raise ValueError(
                    f'Invalid value: {value}. Possible values: {VISIBILITY_GROUP_ENTITY_SETTINGS}')
        return v


class IUpdate(VisibilityGroupBase, BaseUUIDModel):
    prefix: Optional[str]
    admin: Optional[UUID]
    opportunity: Optional[List[str]]
    seller: Optional[List[str]]
    activity: Optional[List[str]]
    property: Optional[List[str]]

    @validator('prefix')
    def prefix_attr_normalization(cls, v):
        if not v:
            return v
        return v.lower().strip().strip('/')

    @validator('opportunity')
    def opportunity_validation(cls, v):
        if v == []:
            raise ValueError('Empty list is not allowed')
        if not v:
            return v
        v = list(map(lambda x: x.lower().strip(), v))
        for value in v:
            if value not in VISIBILITY_GROUP_ENTITY_SETTINGS:
                raise ValueError(
                    f'Invalid value: {value}. Possible values: {VISIBILITY_GROUP_ENTITY_SETTINGS}')
        return v


class IFilter(VisibilityGroupBase):
    ...


class UserIdentity(TypedDict, total=False):
    id: UUID
    email: str


class IVisibilityGroupSettings(BaseModel):
    id: UUID
    admin: Union[UUID, None]
    prefix: str
    user: List[UserIdentity]
    opportunity: List[str]
    seller: List[str]
    activity: List[str]
    property: List[str]


class IVisibilityGroupValidateResponse(BaseModel):
    users: Union[List[UserIdentity], None]
