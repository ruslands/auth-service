# # Native # #
from typing import List

# # Installed # #
from pydantic import BaseModel, validator

# # Package # #
from app.user.model import UserBase
from app.team.model import TeamBase
from core.base.model import BaseUUIDModel


class IRead(TeamBase, BaseUUIDModel):
    users: List[UserBase]


class ICreate(BaseModel):
    title: str

    @validator("title")
    def str_attr_normalization(cls, v):
        return v.lower().strip().strip("/")


class IUpdate(TeamBase, BaseUUIDModel):
    ...


class IFilter(TeamBase):
    ...
