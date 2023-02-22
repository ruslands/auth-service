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
    IAM_TOKEN = "t1.9euelZqJkoucnpiXipSPzZbLkc6Yie3rnpWals6Yy5CTycjNlozOlcjIkonl8_dCOyhg-e8REz1r_d3z9wJqJWD57xETPWv9.399ifZ20AwuhNZSlQteoutvwtv1lzMyA6mR0nhPH0El9-HaAArhD2JHQQoi12O_kgeTLgCwSSoWnG-_h1jxtDw"
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
