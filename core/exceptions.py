from fastapi import HTTPException, status as statuscode

from core.errors import BaseError, ConflictError, NotFoundError
from core.logger import logger


__all__ = (
    "BaseAPIException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundException",
    "BadRequestException",
    "ConflictException",
    "ValidationException",
)


class BaseAPIException(HTTPException):
    """Base error for custom API exceptions"""

    detail = "Generic error"
    status_code = statuscode.HTTP_500_INTERNAL_SERVER_ERROR
    headers = {"X-UI-TOAST": "false"}
    model = BaseError

    def __init__(self, **kwargs):
        self.detail = kwargs.get("detail", self.detail)
        logger.error(f"Exception: {self.detail}")
        super().__init__(status_code=self.status_code, detail=self.detail, headers=self.headers)


class BadRequestException(BaseAPIException):
    """Error raised when a user doing something wrong"""

    detail = "Bad request"
    headers = {"X-UI-TOAST": "true"}
    status_code = statuscode.HTTP_400_BAD_REQUEST


class UnauthorizedException(BaseAPIException):
    """The exception for denied access request."""

    detail = "Unauthorized"
    headers = {"X-UI-TOAST": "false"}
    status_code = statuscode.HTTP_401_UNAUTHORIZED


class ForbiddenException(BaseAPIException):
    """The exception for denied access request."""

    detail = "Access denied"
    headers = {"X-UI-TOAST": "true"}
    status_code = statuscode.HTTP_403_FORBIDDEN


class NotFoundException(BaseAPIException):
    detail = "The entity does not exist"
    headers = {"X-UI-TOAST": "true"}
    status_code = statuscode.HTTP_404_NOT_FOUND
    model = NotFoundError


class ConflictException(BaseAPIException):
    detail = "The entity already exists"
    headers = {"X-UI-TOAST": "true"}
    status_code = statuscode.HTTP_409_CONFLICT
    model = ConflictError


class ApplicationException(BaseAPIException):
    detail = "Application error"
    headers = {"X-UI-TOAST": "true"}
    status_code = statuscode.HTTP_500_INTERNAL_SERVER_ERROR


class ValidationException(BaseAPIException):
    detail = "Validation error"
    headers = {"X-UI-TOAST": "true"}
    status_code = statuscode.HTTP_422_UNPROCESSABLE_ENTITY
