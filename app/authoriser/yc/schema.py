# # Native # #

# # Installed # #
from pydantic import BaseModel, root_validator


__all__ = (
    "RequestVersion",
    "ResponseVersion",
)


class RequestVersion(BaseModel):
    """
    Structure of request described in docs:
    https://cloud.yandex.ru/docs/api-gateway/concepts/extensions/function-authorizer
    """

    path: str
    httpMethod: str
    headers: dict
    queryStringParameters: dict
    pathParameters: dict
    requestContext: dict
    cookies: dict

    class Config:
        extra = "allow"
        allow_mutation: True

    @root_validator
    def parse_request_context(cls, values):
        values["resource"] = values["path"]
        return values


class ResponseVersion(BaseModel):
    """
    Structure of response described in docs:
    https://cloud.yandex.ru/docs/api-gateway/concepts/extensions/function-authorizer
    """

    isAuthorized: bool
    context: dict
