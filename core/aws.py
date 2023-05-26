# # Native # #
import json
import base64

# # Installed # #
import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError

# # Package # #
from core.logger import logger

__all__ = (
    "get_secret",
    "get_lambda_client",
)


REGION_NAME = "us-east-1"


def get_secret(secret_name):
    # logger.debug(f"function get_secret invoked; secret_name: {secret_name}")
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=REGION_NAME
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        # logger.debug(f"get_secret_value_response: {get_secret_value_response}")
    except ClientError as e:
        logger.error(f"Failed to get secret value: {e}")
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = json.loads(get_secret_value_response['SecretString'])
            # logger.debug(f"Received SecretString: {secret}")
            return secret
        else:
            secret = base64.b64decode(
                get_secret_value_response['SecretBinary'])
            # logger.debug(f"Received SecretBinary: {secret}")
            return secret


def get_lambda_client() -> BaseClient:
    session = boto3.session.Session()
    return session.client(
        service_name='lambda',
        region_name=REGION_NAME
    )
