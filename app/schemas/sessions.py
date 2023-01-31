# # Native # #
from uuid import UUID

# # Installed # #
from pydantic import BaseModel

# # Package # #
from app.models.sessions import SessionsBase

__all__ = (
    "ICreate",
    "IRead",
    "IUpdate",
)


class ICreate(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_at: int
    user_id: UUID


class IUpdate(BaseModel):
    id: UUID
    access_token: str
    refresh_token: str
    access_token_expires: int
    refresh_token_expires: int


class IRead(SessionsBase):
    id: UUID
