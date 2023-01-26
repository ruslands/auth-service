# # Native # #

# # Installed # #
from pydantic import BaseModel, Field

# # Package # #


__all__ = (
    "BaseError",
    "BaseIdentifiedError",
    "NotFoundError",
    "AlreadyExistsError"
)


class BaseError(BaseModel):
    detail: str = Field(..., description="Error detail or description")


class BaseIdentifiedError(BaseError):
    ...
    # identifier: str = Field(..., description="Unique identifier which this error references to")


class NotFoundError(BaseIdentifiedError):
    """The entity does not exist"""
    pass


class AlreadyExistsError(BaseIdentifiedError):
    """An entity being created already exists"""
    pass
