# # Native # #
from typing import List, Optional
from uuid import UUID


# # Installed # #
from sqlalchemy import String
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, Relationship, SQLModel, Column

# # Package # #
from core.base.model import BaseUUIDModel

__all__ = (
    "Visibility_Group",
)


class VisibilityGroupBase(SQLModel):
    prefix: str = Field(index=True, sa_column_kwargs={"unique": True})
    admin: Optional[UUID] = Field(sa_column_kwargs={"unique": True})
    opportunity: Optional[List[str]] = Field(
        default=None, sa_column=Column(postgresql.ARRAY(String())))
    seller: Optional[List[str]] = Field(
        default=None, sa_column=Column(postgresql.ARRAY(String())))
    activity: Optional[List[str]] = Field(
        default=None, sa_column=Column(postgresql.ARRAY(String())))
    property: Optional[List[str]] = Field(
        default=None, sa_column=Column(postgresql.ARRAY(String())))


class Visibility_Group(BaseUUIDModel, VisibilityGroupBase, table=True):
    __table_args__ = {
        'comment': 'Visibility Group',
        "schema": "auth"
    }
    user: List["User"] = Relationship(
        sa_relationship_kwargs={'uselist': True}, back_populates="visibility_group")
