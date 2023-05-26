# # Native # #
from datetime import date, timedelta, datetime
from typing import Generic, List, Optional, TypeVar

# # Installed # #
from pydantic.generics import GenericModel
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, root_validator

# # Package # #
from app.role.schema import IRead

__all__ = (
    "IGetResponseBase",
    "IPostResponseBase",
    "IPutResponseBase",
    "IDeleteResponseBase",
    "IMetaGeneral",
)

DataType = TypeVar("DataType")


class BaseMeta(BaseModel):
    pass


class IResponseBase(GenericModel, Generic[DataType]):
    message: str = ""
    meta: dict | BaseMeta = {}
    data: Optional[DataType] = None


class IGetResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str = "Data got correctly"


class IPostResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str = "Data created correctly"


class IPutResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str = "Data updated correctly"


class IDeleteResponseBase(IResponseBase[DataType], Generic[DataType]):
    message: str = "Data deleted correctly"

class IMetaGeneral(BaseModel):
    roles: List[IRead]

class BaseFilter(BaseModel):
    date_start: Optional[date]
    date_end: Optional[date]

    @root_validator
    def validate_date(cls, v):
        if v["date_start"] is None and v["date_end"]:
            raise ValueError("Specify the start date")
        if not isinstance(v["date_end"], datetime):
            v["date_end"] = datetime.now().date() + timedelta(days=1)
        return v
