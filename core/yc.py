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

### yandex cloud ###

def get_secret(secret_name):
    try:
        httpx.get(
            f"https://payload.lockbox.api.cloud.yandex.net/lockbox/v1/secrets/{secret_id}/payload",
            headers={"Authorization": f"Bearer {IAM_TOKEN}"}
            )
    except Exception as e:
        logger.error(f"Failed to get secret value: {e}")
        raise e
    else:
        return secret
