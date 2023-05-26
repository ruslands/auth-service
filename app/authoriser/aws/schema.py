# # Native # #
from typing import Optional, Literal, List

# # Installed # #
from pydantic import BaseModel, root_validator


__all__ = (
    'RequestVersion1',
    'RequestVersion2',
    'ResponseVersion2',
)


class RequestVersion1(BaseModel):
    version: Literal['1.0']
    type: str
    methodArn: str
    identitySource: str
    authorizationToken: str
    resource: str
    path: str
    httpMethod: str
    headers: dict
    queryStringParameters: dict
    pathParameters: dict
    stageVariables: dict
    requestContext: dict

    class Config:
        extra = 'allow'
        allow_mutation: True

    @root_validator
    def parse_method_arn(cls, values):
        values['methodArn']: List[str] = values['methodArn'].split(':')
        values['awsRegion']: str = values['methodArn'][3]
        values['awsAccountId']: str = values['methodArn'][4]
        values['awsApiGateway']: str = values['methodArn'][5].split('/')
        values['awsRestApiId']: str = values['awsApiGateway'][0]
        values['awsStage']: str = values['awsApiGateway'][1]
        return values


class RequestVersion2(BaseModel):
    version: Literal['2.0']
    type: str
    routeArn: str
    identitySource: List[str]
    routeKey: str
    rawPath: str
    rawQueryString: str
    cookies: Optional[List[str]]
    headers: dict
    queryStringParameters: dict
    pathParameters: dict
    stageVariables: Optional[dict]
    requestContext: dict

    class Config:
        extra = 'allow'
        allow_mutation: True

    @root_validator
    def parse_request_context(cls, values):
        values['httpMethod']: str = values['requestContext']['http']['method']
        values['resource']: str = values['requestContext']['http']['path']
        return values


class ResponseVersion2(BaseModel):
    isAuthorized: bool
    context: dict
