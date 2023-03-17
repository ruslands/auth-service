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
    IAM_TOKEN = "t1.9euelZqZy56dz4yQyI7IkZOLms2az-3rnpWals6Yy5CTycjNlozOlcjIkonl9PcTQE5f-e8dZVz63fT3U25LX_nvHWVc-g.kjQ_T6dXpoHKYKz8pk8zmFk8BIdTbCoxm2YEiQJqjTUDiLdfmsd9k1n3fZySGwEEAzymVeh00lWHa4fwZ8W5Cw"
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
