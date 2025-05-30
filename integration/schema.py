from typing import Generic, Optional, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class DefaultErrorResponse(BaseModel):
    error: str


class APIResponse(BaseModel, Generic[T]):
    data: Optional[T]
    status_code: int
