# # Native # #
from typing import List

# # Installed # #
from pydantic import BaseModel, validator

# # Package # #
from app.models.user import UserBase
from app.models.team import TeamBase
from app.models.base_uuid_model import BaseUUIDModel


class ITeamRead(TeamBase, BaseUUIDModel):
    ...


class ITeamCreate(BaseModel):
    name: str

    @validator('name')
    def str_attr_normalization(cls, v):
        return v.lower().strip().strip('/')


class ITeamUpdate(TeamBase, BaseUUIDModel):
    ...


class ITeamReadWithUsers(ITeamRead):
    users: List[UserBase]
