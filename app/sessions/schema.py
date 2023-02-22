# # Native # #
from uuid import UUID

# # Installed # #
from pydantic import BaseModel

# # Package # #
from app.sessions.model import SessionsBase
from core.base.model import BaseUUIDModel

__all__ = (
    "ICreate",
    "IRead",
    "IUpdate",
)


class ICreate(SessionsBase):
    ...


class IUpdate(SessionsBase):
    ...


class IRead(SessionsBase, BaseUUIDModel):
    ...
