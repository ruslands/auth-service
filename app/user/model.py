# # Native # #
from uuid import UUID
from typing import List, Optional, Set

# # Installed # #
from pydantic import EmailStr, AnyHttpUrl
from sqlalchemy import String, Boolean
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import expression
from sqlmodel import Field, SQLModel, Relationship, Column

# # Package # #
from app.common.links import LinkRoleUser, LinkTeamUser
from core.base.model import BaseUUIDModel


__all__ = ("User",)


class UserBase(SQLModel):
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    email: Optional[EmailStr] = Field(index=True, unique=True)
    hashed_password: Optional[str] = None
    is_active: Optional[bool] = Field(
        sa_column=Column(
            "is_active", Boolean, server_default=expression.true(), nullable=False
        )
    )
    is_staff: Optional[bool] = Field(
        sa_column=Column(
            "is_staff", Boolean, server_default=expression.false(), nullable=False
        )
    )
    is_superuser: Optional[bool] = Field(
        sa_column=Column(
            "is_superuser", Boolean, server_default=expression.false(), nullable=False
        )
    )
    allow_basic_login: Optional[bool] = Field(
        sa_column=Column(
            "allow_basic_login",
            Boolean,
            server_default=expression.false(),
            nullable=False,
        )
    )
    aliases: Optional[Set[str]] = Field(
        sa_column=Column("aliases", postgresql.ARRAY(String()))
    )
    picture: Optional[AnyHttpUrl] = Field(nullable=True)
    visibility_group_id: Optional[UUID] = Field(
        foreign_key="auth.visibility_group.id", index=True
    )

    class Config:
        extra = "allow"


class User(BaseUUIDModel, UserBase, table=True):
    __table_args__ = {"comment": "User", "schema": "auth"}
    roles: List["Role"] = Relationship(
        back_populates="users", link_model=LinkRoleUser,
        sa_relationship_kwargs={
            "lazy": "selectin"
        })
    teams: List["Team"] = Relationship(
        back_populates="users", link_model=LinkTeamUser,
        sa_relationship_kwargs={
            "lazy": "selectin"
        })
    sessions: List["Sessions"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "cascade": "delete",
            "uselist": True, "lazy": "selectin"
        },
    )
    visibility_group: "Visibility_Group" = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "uselist": False, "lazy": "selectin"
        }
    )


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
# accepted_privacy_policy
# accepted_privacy_policy_timestamp
# accepted_privacy_policy_ip
# accepted_terms_of_use
# accepted_terms_of_use_timestamp
# accepted_terms_of_use_ip
# reason_of_blocking
