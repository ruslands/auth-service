# # Native # #
from uuid import UUID
from typing import List, Optional, Set

# # Installed # #
from pydantic import EmailStr
from sqlalchemy import String
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, SQLModel, Relationship, Column

# # Package # #
from app.models.links import LinkRoleUser, LinkTeamUser
from app.models.base_uuid_model import BaseUUIDModel


__all__ = (
    "User",
)


class UserBase(SQLModel):
    first_name: str
    last_name: str
    full_name: str
    email: EmailStr = Field(nullable=False, index=True, sa_column_kwargs={"unique": True})
    hashed_password: Optional[str] = Field(nullable=False)
    is_active: bool = Field(default=False)
    is_staff: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    allow_basic_login: bool = Field(default=False)
    phone: Optional[str]
    country: Optional[str]
    aliases: Optional[Set[str]] = Field(
        default=None, sa_column=Column(postgresql.ARRAY(String())))

    class Config:
        extra = 'allow'


class User(BaseUUIDModel, UserBase, table=True):
    roles: List["Role"] = Relationship(back_populates="users", link_model=LinkRoleUser)
    teams: List["Team"] = Relationship(back_populates="users", link_model=LinkTeamUser)
    sessions: List["Sessions"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "delete", 'uselist': True})
    visibility_group_id: Optional[UUID] = Field(default=None, foreign_key="visibility_group.id", index=True, sa_column_kwargs={"unique": False})
    visibility_group: "Visibility_Group" = Relationship(back_populates="user", sa_relationship_kwargs={'uselist': False})


# device_id
# system_device_id
# idfa
# platform
# model
# version
# orders_count
# spendings
# cashback_available
# cashback_used
# accepted_ptivacy_policy
# accepted_ptivacy_policy_timestamp
# accepted_privacy_policy_ip
# accepted_terms_of_use
# accepted_terms_of_use_timestamp
# accepted_terms_of_use_ip
# reason_of_blocking

