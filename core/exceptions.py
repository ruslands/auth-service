# # Installed # #
from fastapi import HTTPException
from fastapi import status as statuscode
from fastapi.responses import JSONResponse

# # Package # #
from core.errors import BaseError, BaseIdentifiedError, NotFoundError, AlreadyExistsError
from core.logger import logger


__all__ = (
    "BaseAPIException",
    "BaseIdentifiedException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundException",
    "BadRequestException",
    "ConflictException",
    "AlreadyExistsException",
)


class BaseAPIException(HTTPException):
    """Base error for custom API exceptions"""
    detail = "Generic error"
    status_code = statuscode.HTTP_500_INTERNAL_SERVER_ERROR
    model = BaseError

    def __init__(self, **kwargs):
        kwargs.setdefault("detail", self.detail)
        self.detail = kwargs["detail"]
        self.data = self.model(**kwargs)
        logger.error(f"Exception: {self.detail}")

    def __str__(self):
        return self.detail

    def response(self):
        return JSONResponse(
            content=self.data.dict(),
            status_code=self.status_code
        )

    @classmethod
    def response_model(cls):
        return {cls.status_code: {"model": cls.model}}


class BaseIdentifiedException(BaseAPIException):
    """Base error for exceptions related with entities, uniquely identified"""
    detail = "Entity error"
    status_code = statuscode.HTTP_500_INTERNAL_SERVER_ERROR
    model = BaseIdentifiedError

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # def __init__(self, identifier, **kwargs):
    #     super().__init__(identifier=identifier, **kwargs)


class BadRequestException(BaseIdentifiedException):
    """Error raised when a user doing something wrong"""
    detail = "Bad request"
    status_code = statuscode.HTTP_400_BAD_REQUEST


class UnauthorizedException(BaseIdentifiedException):
    """The exception for denied access request."""
    detail = "Unauthorized"
    status_code = statuscode.HTTP_401_UNAUTHORIZED


class ForbiddenException(BaseIdentifiedException):
    """The exception for denied access request."""
    detail = "Access denied"
    status_code = statuscode.HTTP_403_FORBIDDEN


class NotFoundException(BaseIdentifiedException):
    """Base error for exceptions raised because an entity does not exist"""
    detail = "The entity does not exist"
    status_code = statuscode.HTTP_404_NOT_FOUND
    model = NotFoundError


class ConflictException(BaseIdentifiedException):
    """Base error for exceptions raised because an entity already exists"""
    detail = "The entity already exists"
    status_code = statuscode.HTTP_409_CONFLICT
    model = AlreadyExistsError


class AlreadyExistsException(BaseIdentifiedException):
    """Base error for exceptions raised because an entity already exists"""
    detail = "The entity already exists"
    status_code = statuscode.HTTP_409_CONFLICT
    model = AlreadyExistsError
