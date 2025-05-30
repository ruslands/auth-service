import base64
import json

import boto3
from botocore.exceptions import ClientError

from core.logger import logger


__all__ = ("get_secret",)


def get_secret(secret_name):
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        logger.error(f"Failed to get secret value: {e}")
        raise e
    else:
        if "SecretString" in get_secret_value_response:
            secret = json.loads(get_secret_value_response["SecretString"])
            return secret
        else:
            secret = base64.b64decode(get_secret_value_response["SecretBinary"])
            return secret
