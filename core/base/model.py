# # Native # #
from typing import Optional
from uuid import UUID
from datetime import datetime

# # Installed # #
from sqlmodel import SQLModel, Field
from sqlalchemy import TIMESTAMP, Column, func, text
from sqlalchemy.dialects.postgresql import UUID as uuid

__all__ = ("BaseUUIDModel",)


class BaseUUIDModel(SQLModel):
    id: Optional[UUID] = Field(
        sa_column=Column(
            uuid(as_uuid=True),
            primary_key=True,
            index=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(
            TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp()
        ),
        index=True,
    )
    created_at: Optional[datetime] = Field(
        sa_column=Column(TIMESTAMP, server_default=func.now()), index=True
    )
    updated_by: Optional[UUID]  # = Field(default=None, foreign_key="user.id") #TODO
    created_by: Optional[UUID]  # = Field(default=None, foreign_key="user.id") #TODO
    description: Optional[str] = Field(default=None)
    # changelog: Optional[List[str]]
