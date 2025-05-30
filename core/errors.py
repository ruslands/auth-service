from pydantic import BaseModel, Field


__all__ = ("BaseError", "BaseIdentifiedError", "NotFoundError", "ConflictError")


class BaseError(BaseModel):
    detail: str = Field(..., description="Error detail or description")


class BaseIdentifiedError(BaseError):
    ...
    # identifier: str = Field(..., description="Unique identifier which this error references to")


class NotFoundError(BaseIdentifiedError):
    """The entity does not exist"""

    pass


class ConflictError(BaseIdentifiedError):
    """An entity being created already exists"""

    pass
