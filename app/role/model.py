# # Native # #
from typing import List, Optional

# # Installed # #
from sqlalchemy import Boolean
from sqlalchemy.sql import expression
from sqlmodel import SQLModel, Relationship, Field, Column

# # Package # #
from core.base.model import BaseUUIDModel
from app.common.links import LinkRoleUser
from app.permission.model import Permission

__all__ = (
    "Role",
)


class RoleBase(SQLModel):
    title: str = Field(nullable=True, unique=True)
    default: Optional[bool] = Field(sa_column=Column(
        "default", Boolean, server_default=expression.false(), nullable=False))


class Role(BaseUUIDModel, RoleBase, table=True):
    __table_args__ = {
        'comment': 'Role',
        "schema": "auth"
    }
    users: Optional[List["User"]] = Relationship(
        back_populates="roles", link_model=LinkRoleUser,
        sa_relationship_kwargs={
            "lazy": "selectin"
        }
    )
    resources: Optional[List["Resource"]] = Relationship(
        back_populates="roles", link_model=Permission,
        sa_relationship_kwargs={
            "lazy": "selectin"
        }
    )
