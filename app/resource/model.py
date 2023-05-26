# # Native # #
from typing import List, Optional

# # Installed # #
from sqlmodel import SQLModel, Relationship, Field

# # Package # #
from app.permission.model import Permission
from core.base.model import BaseUUIDModel


__all__ = (
    "Resource",
    "ResourceBase"
)


class ResourceBase(SQLModel):
    endpoint: str = Field(index=True, sa_column_kwargs={"unique": False})
    method: str = Field(index=True, sa_column_kwargs={"unique": False})
    rbac_enable: Optional[bool] = Field(default=False)
    visibility_group_enable: Optional[bool] = Field(default=False)
    visibility_group_entity: Optional[str] = Field(default=None)


class Resource(BaseUUIDModel, ResourceBase, table=True):
    __table_args__ = {
        'comment': 'Resource',
        "schema": "auth"
    }
    roles: Optional[List["Role"]] = Relationship(
        back_populates="resources", link_model=Permission)
