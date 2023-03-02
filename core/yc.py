# # Native # #
import json
import base64

# # Installed # #
import httpx

# # Package # #
from core.logger import logger

__all__ = (
    "get_secret",
)


def get_secret(secret_name):
    IAM_TOKEN = "t1.9euelZrIjJKOiszKkZCcnJaMjp7Mku3rnpWals6Yy5CTycjNlozOlcjIkonl9Pc-OH5f-e8rR1H13fT3fmZ7X_nvK0dR9Q.nQxDXho3ynytIbRn_wYjU6kkz6AgMFxRxJk7jcFHSwY7YYgP3py3RdTdbPR0PDZV6g4aB_caCfflXreykUHfDQ"
    try:
        response = httpx.get(
            secret_name,
            headers={
                "Authorization": f"Bearer {IAM_TOKEN}"
                }
            )
        if response.status_code != 200:
            raise Exception
        response = response.json()
        secrets = {item['key']:item['textValue'] for item in response['entries']}
    except Exception as e:
        logger.error(f"failed to fetch the secrets: {e}")
        raise e
    else:
        return secrets
