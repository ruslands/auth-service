# # Native # #
from typing import Optional, List, Union
from uuid import UUID
from datetime import datetime

# # Installed # #
from pydantic import BaseModel, EmailStr, validator, root_validator

# # Package # #
from app.user.model import UserBase
from core.security import get_password_hash, create_password
from .role import IRead
from .team import IRead
from .sessions import IRead
from .visibility_group import IRead

__all__ = (
    "ICreate",
    "IRead",
    "IUpdate",
    "IReadTemporary",
)


class IUserFilter(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    email: Optional[EmailStr]
    is_active: Optional[bool]
    phone: Optional[str]
    region: Optional[Union[str, List[str]]]

    @validator('region')
    def region_must_be_list(cls, v):
        if isinstance(v, str):
            return [v.lower().strip()]


class ICreate(BaseModel):
    first_name: str
    last_name: str
    full_name: Optional[str]
    email: EmailStr
    phone: Optional[str]
    country: Optional[str]
    city: Optional[str]
    title: Optional[str]
    region: Optional[List]

    @validator('email', 'country', 'city')
    def str_attr_must_be_lower(cls, v):
        return v.lower().strip()

    @root_validator
    def create_password(cls, values):
        values["password"] = create_password()
        return values

    @root_validator
    def create_hashed_password(cls, values):
        values["hashed_password"] = get_password_hash(values["password"])
        return values

    @root_validator
    def create_full_name(cls, values):
        values["full_name"] = f"{values['first_name']} {values['last_name']}"
        return values

    @root_validator
    def activate_user(cls, values):
        values["is_active"] = True
        return values

class IReadTemporary(UserBase):  # TODO use IRead
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    email: Optional[EmailStr]
    id: Optional[UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    visibility_group_id: Optional[Union[UUID, None]]

    @root_validator
    def remove_sensitive_data(cls, values):
        if "hashed_password" in values:
            del values["hashed_password"]
        return values

    @root_validator
    def remove_excluded_fields(cls, values):
        if hasattr(cls, '__exclude_fields_custom__'):
            for field in cls.__exclude_fields_custom__:
                if field in values:
                    del values[field]
        return values


class IRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    roles: Optional[List[IRead]]
    teams: Optional[List[IRead]]
    sessions: Optional[List[IRead]]
    visibility_group: Optional[IRead]

    @root_validator
    def remove_sensitive_data(cls, values):
        if "hashed_password" in values:
            del values["hashed_password"]
        return values


class IUpdate(BaseModel):
    team_id: Optional[UUID]
    phone: Optional[str]
    country: Optional[str]
    city: Optional[str]
    title: Optional[str]
    email: Optional[EmailStr]
    region: Optional[List]
    is_active: Optional[bool]
    is_staff: Optional[bool]
    is_superuser: Optional[bool]
    allow_basic_login: Optional[bool]
