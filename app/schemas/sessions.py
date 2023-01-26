# # Native # #
from uuid import UUID

# # Installed # #
from pydantic import BaseModel

# # Package # #
from app.models.sessions import SessionsBase

__all__ = (
    "ISessionsCreate",
    "ISessionsRead",
    "ISessionsUpdate",
)


class ISessionsCreate(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_at: int
    user_id: UUID


class ISessionsUpdate(BaseModel):
    id: UUID
    access_token: str
    refresh_token: str
    access_token_expires: int
    refresh_token_expires: int


class ISessionsRead(SessionsBase):
    id: UUID
