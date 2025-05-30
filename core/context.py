from typing import Optional
from uuid import UUID

from fastapi import Request
from pydantic import BaseModel


__all__ = "IContext"


class IContext(BaseModel):
    email: Optional[str] = None
    user_id: Optional[UUID] = None
    task_name: Optional[UUID] = None


def get_context(request: Request) -> IContext:
    return IContext(**request.scope["context"])
