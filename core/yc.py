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
    IAM_TOKEN = "t1.9euelZqYjJCQkJjJkcaanMuNm5yVye3rnpWals6Yy5CTycjNlozOlcjIkonl8_cIaHhf-e8hOS51_t3z90gWdl_57yE5LnX-.45t1kpIkTrVlM_UZVPO6aXkpWt2nxsZwto5CLEbggt1uTpfy016SqRtXCgAjhEqbWekNcFa8CC-LCWPa8uqmAw"
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
