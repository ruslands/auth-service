# # Native # #
from typing import Optional
import uuid as uuid_pkg
from uuid import UUID
from datetime import datetime

# # Installed # #
from sqlmodel import SQLModel, Field
from sqlalchemy import TIMESTAMP, Column, func

__all__ = (
    "BaseUUIDModel",
)


class BaseUUIDModel(SQLModel):
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    updated_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()), index=True)
    created_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP, server_default=func.now()), index=True)
    updated_by: Optional[UUID]  # = Field(default=None, foreign_key="user.id") #TODO
    created_by: Optional[UUID]  # = Field(default=None, foreign_key="user.id") #TODO
    description: Optional[str] = Field(default=None)
    # changelog: Optional[List[str]]
