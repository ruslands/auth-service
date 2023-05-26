
# # Native # #
from uuid import UUID
from typing import Optional
from datetime import datetime
import uuid as uuid_pkg

# # Installed # #
from sqlmodel import SQLModel, Field
from sqlalchemy import TIMESTAMP, Column, func

__all__ = (
    "Permission",
)


class PermissionBase(SQLModel):
    id: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=False,
        index=True,
        nullable=False,
    )
    updated_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()), index=True)
    created_at: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP, server_default=func.now()), index=True)
    # = Field(default=None, foreign_key="user.id") #TODO
    updated_by: Optional[UUID]
    # = Field(default=None, foreign_key="user.id") #TODO
    created_by: Optional[UUID]
    title: Optional[str]
    description: Optional[str]
    role_id: UUID = Field(
        default=None, nullable=False,
        foreign_key="auth.role.id", primary_key=True
    )
    resource_id: UUID = Field(
        default=None, nullable=False,
        foreign_key="auth.resource.id", primary_key=True
    )


class Permission(PermissionBase, table=True):
    __table_args__ = {
        'comment': 'Permission',
        "schema": "auth"
    }
    ...
