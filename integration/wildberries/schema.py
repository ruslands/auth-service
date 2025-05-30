from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UploadTaskPriceData(BaseModel):
    id: int
    alreadyExists: bool


class UploadTaskPriceResponse(BaseModel):
    data: Optional[UploadTaskPriceData] = None
    error: bool
    errorText: str


class UploadTaskPriceErrorResponse(BaseModel):
    title: Optional[str]
    detail: Optional[str]
    code: Optional[str]
    requestId: Optional[str]
    origin: Optional[str]
    status: Optional[str]
    statusText: Optional[str]
    timestamp: Optional[datetime]
