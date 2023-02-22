# # Native # #
from typing import List, Optional

# # Installed # #
from sqlmodel import SQLModel, Relationship, Field

# # Package # #
from app.models.base_uuid_model import BaseUUIDModel
from app.models.links import LinkRoleUser
from app.models.permission import Permission

__all__ = (
    "Role",
)


class RoleBase(SQLModel):
    name: str = Field(nullable=True, index=False, sa_column_kwargs={"unique": True})
    default: Optional[bool] = Field(default=False)


class Role(BaseUUIDModel, RoleBase, table=True):
    users: Optional[List["User"]] = Relationship(
        back_populates="roles", link_model=LinkRoleUser)
    resources: Optional[List["Resource"]] = Relationship(
        back_populates="roles", link_model=Permission)
