# # Native # #
import json
import os

# # Installed # #
import yandexcloud
from yandex.cloud.lockbox.v1.payload_service_pb2 import GetPayloadRequest
from yandex.cloud.lockbox.v1.payload_service_pb2_grpc import PayloadServiceStub

# # Package # #
from core.logger import logger

__all__ = (
    "get_secret",
)

ENV_KEY_YC_AUTH_METHOD = "YC_AUTH_METHOD"
ENV_KEY_YC_SA_KEY = "YC_SA_KEY"
ENV_KEY_YC_IAM_TOKEN = "YC_IAM_TOKEN"
ENV_KEY_YC_OAUTH_TOKEN = "YC_OAUTH_TOKEN"


class YCAuthMethod:
    """
    Possible values of YC_AUTH_METHOD environment variable.
    """
    YC_AUTH_METHOD_BY_SA_KEY = "YC_AUTH_BY_SA_KEY"
    YC_AUTH_METHOD_BY_IAM_TOKEN = "YC_AUTH_BY_IAM_TOKEN"
    YC_AUTH_METHOD_BY_OAUTH_TOKEN = "YC_AUTH_BY_OAUTH_TOKEN"


def get_secret(secret_id: str) -> dict:
    """
    Authorization method is determined by the YC_AUTH_METHOD environment variable.

    YC_AUTH_METHOD can be one of the following:
    - YC_AUTH_BY_SA_KEY - presented as a JSON string which contains next data:
        {
            "id": "...",
            "service_account_id": "...",
            "private_key": "..."
        }
    - YC_AUTH_BY_OAUTH_TOKEN - presented as a string
    - YC_AUTH_BY_IAM_TOKEN - presented as a string
    - DEFAULT - default behaviour is used for executing code inside VMs or Cloud Functions running in Yandex.Cloud.
    """
    try:
        match os.getenv(ENV_KEY_YC_AUTH_METHOD):
            case YCAuthMethod.YC_AUTH_METHOD_BY_SA_KEY:
                # The best choice for running code outside Yandex.Cloud.
                yc_sdk = yandexcloud.SDK(service_account_key=json.loads(os.environ[ENV_KEY_YC_SA_KEY]))
            case YCAuthMethod.YC_AUTH_METHOD_BY_OAUTH_TOKEN:
                yc_sdk = yandexcloud.SDK(token=os.environ[ENV_KEY_YC_OAUTH_TOKEN])
            case YCAuthMethod.YC_AUTH_METHOD_BY_IAM_TOKEN:
                yc_sdk = yandexcloud.SDK(iam_token=os.environ[ENV_KEY_YC_IAM_TOKEN])
            case _:
                # The best choice for running code inside VMs or Cloud Functions running in Yandex.Cloud.
                yc_sdk = yandexcloud.SDK()

        lockbox = yc_sdk.client(PayloadServiceStub)
        response = lockbox.Get(GetPayloadRequest(secret_id=secret_id))

        return {
            entry.key: entry.text_value
            for entry in response.entries
        }
    except Exception as e:
        logger.error(f"Failed to get secret value: {e}")
        raise e
