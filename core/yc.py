# # Native # #
from enum import Enum

# # Installed # #
import httpx
import yandexcloud
from yandex.cloud.lockbox.v1.payload_service_pb2 import GetPayloadRequest
from yandex.cloud.lockbox.v1.payload_service_pb2_grpc import PayloadServiceStub

# # Package # #
from core.logger import logger

__all__ = (
    "get_secret",
    "YCAuthMethod"
)


class YCAuthMethod(str, Enum):
    """
    Possible values of YC_AUTH_METHOD environment variable.
    """
    YC_AUTH_BY_SERVICE_ACCOUNT_KEY = "YC_AUTH_BY_SERVICE_ACCOUNT_KEY"
    YC_AUTH_BY_IAM_TOKEN = "YC_AUTH_BY_IAM_TOKEN"
    YC_AUTH_BY_OAUTH_TOKEN = "YC_AUTH_BY_OAUTH_TOKEN"


def get_access_token():
    metadata_server = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    metadata_flavor = {'Metadata-Flavor': 'Google'}
    access_data = httpx.get(metadata_server, headers=metadata_flavor).json()
    return access_data.get("access_token")


def get_secret(secret_id: str, YC_AUTH_METHOD: str, YC_CREDENTIALS: str) -> dict:
    """
    Authorization method is determined by the YC_AUTH_METHOD environment variable.

    YC_AUTH_METHOD can be one of the following:
    - YC_AUTH_BY_SERVICE_ACCOUNT_KEY - presented as a JSON string which contains next data:
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
        match YC_AUTH_METHOD:
            case YCAuthMethod.YC_AUTH_BY_SERVICE_ACCOUNT_KEY:
                # The best choice for running code outside Yandex.Cloud.
                yc_sdk = yandexcloud.SDK(service_account_key=YC_CREDENTIALS)
            case YCAuthMethod.YC_AUTH_BY_OAUTH_TOKEN:
                yc_sdk = yandexcloud.SDK(token=YC_CREDENTIALS)
            case YCAuthMethod.YC_AUTH_BY_IAM_TOKEN:
                # yc_sdk = yandexcloud.SDK(iam_token=YC_CREDENTIALS)
                YC_CREDENTIALS = get_access_token()
                response = httpx.get(
                    url=f"https://payload.lockbox.api.cloud.yandex.net/lockbox/v1/secrets/{secret_id}/payload",
                    headers={"Authorization": f"Bearer {YC_CREDENTIALS}"})
                response = response.json()
                secrets = {item['key']: item['textValue'] for item in response['entries']}
                return secrets
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
