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
    IAM_TOKEN = "t1.9euelZqLzJyLlJmel4-Ly42Yks-Qye3rnpWals6Yy5CTycjNlozOlcjIkonl8_dTBy1g-e9fS3F5_t3z9xM2KmD5719LcXn-.XzWlrSpLQdsSc579t5o210X_QWSeCTwU4LR2mOYHkDB9PHgj28_of6cwUYrJGEh3_fwT8-CxDoP8e36WhOR4CA"
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
