# # Native # #
from typing import List

# # Installed # #
from pydantic import BaseModel, validator

# # Package # #
from app.models.user import UserBase
from app.models.team import TeamBase
from app.models.base_uuid_model import BaseUUIDModel


class IRead(TeamBase, BaseUUIDModel):
    ...


class ICreate(BaseModel):
    name: str

    @validator('name')
    def str_attr_normalization(cls, v):
        return v.lower().strip().strip('/')


class IUpdate(TeamBase, BaseUUIDModel):
    ...


class IReadWithUsers(IRead):
    users: List[UserBase]
