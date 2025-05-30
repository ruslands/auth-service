# # Native # #
from typing import Optional, List, Union, Literal
from uuid import UUID

# # Installed # #
from pydantic import BaseModel, EmailStr, validator, root_validator, AnyHttpUrl

# # Package # #
from app.user.model import UserBase
from core.security import get_password_hash, create_password
from core.logger import logger
from core.base.model import BaseUUIDModel
from core.base.schema import BaseMeta
from app.role.schema import IRead as IReadRole
from app.team.schema import IRead as IReadTeam
from app.sessions.schema import IRead as IReadSessions
from app.visibility_group.schema import IRead as IReadVisibilityGroup

__all__ = (
    "ICreate",
    "IRead",
    "IUpdate",
    "IIdentityProvider",
    "IFilter",
)


class IFilter(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    email: Optional[EmailStr]
    is_active: Optional[bool]
    roles: Optional[Union[str, List[str]]]

    # @validator('region')
    # def region_must_be_list(cls, v):
    #     if isinstance(v, str):
    #         return [v.lower().strip()]


class IIdentityProvider(BaseModel):
    idp: Literal["google", "facebook", "apple", "keycloak"]
    idp_access_token: str
    idp_refresh_token: str

    @validator("idp_access_token")
    def validate_empty(cls, value):
        if not value:
            raise ValueError("Field cannot be empty")
        return value
    
    @validator("idp_refresh_token")
    def validate_refresh_token(cls, token, values):
        if values.get("idp") != "facebook":
            if not token:
                raise ValueError("Field cannot be empty")
        return token


class ICreate(BaseModel):
    first_name: str
    last_name: Optional[str]
    full_name: Optional[str]
    email: EmailStr
    phone: Optional[str]
    country: Optional[str]
    city: Optional[str]
    title: Optional[str]
    region: Optional[List]
    picture: Optional[AnyHttpUrl]

    @validator("email", "country", "city")
    def str_attr_must_be_lower(cls, v):
        return v.lower().strip()

    @root_validator
    def create_password(cls, values):
        values["password"] = create_password()
        logger.debug(
            f"Created password for user {values['email']}: {values['password']}"
        )
        values["allow_basic_login"] = True
        return values

    @root_validator
    def create_hashed_password(cls, values):
        values["hashed_password"] = get_password_hash(values["password"])
        return values

    @root_validator
    def create_full_name(cls, values):
        if "last_name" not in values:
            values["last_name"] = ""
        values["full_name"] = f"{values['first_name']} {values['last_name']}".strip()
        return values

    @root_validator
    def activate_user(cls, values):
        values["is_active"] = True
        return values


class IRead(UserBase, BaseUUIDModel):
    roles: Optional[List[IReadRole]]
    teams: Optional[List[IReadTeam]]
    sessions: Optional[List[IReadSessions]]
    visibility_group: Optional[IReadVisibilityGroup]

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
    country_code: Optional[str]
    phone_confirmation_code: Optional[str]


class IAuthMeta(BaseMeta):
    id: UUID
    first_name: str
    last_name: Optional[str]
    full_name: Optional[str]
    email: EmailStr
    roles: list
    picture: Optional[AnyHttpUrl] = None

    @validator("roles")
    def get_role_title(cls, v):
        return [r.title for r in v]
