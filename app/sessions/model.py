# # Native # #
import uuid
from uuid import UUID
from datetime import datetime

# # Installed # #
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import TIMESTAMP, Column, func

__all__ = (
    "SessionsBase",
    "Sessions",
)


class SessionsBase(SQLModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    cookie: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: int
    created_at: datetime = Field(sa_column=Column(TIMESTAMP, server_default=func.now()))
    user_id: UUID = Field(
        default=None,
        foreign_key="auth.user.id",
        index=False,
        sa_column_kwargs={"unique": False},
    )


class Sessions(SessionsBase, table=True):
    __table_args__ = {"comment": "Sessions", "schema": "auth"}
    user: "User" = Relationship(
        sa_relationship_kwargs={"uselist": False}, back_populates="sessions"
    )
