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

IAM_TOKEN = "t1.9euelZqJkoucnpiXipSPzZbLkc6Yie3rnpWals6Yy5CTycjNlozOlcjIkonl8_dCOyhg-e8REz1r_d3z9wJqJWD57xETPWv9.399ifZ20AwuhNZSlQteoutvwtv1lzMyA6mR0nhPH0El9-HaAArhD2JHQQoi12O_kgeTLgCwSSoWnG-_h1jxtDw"
FOLDER_ID = "folder_id"


def get_secret_id_by_name(secret_name, folder_id):
    secrets_url = f"https://lockbox.api.cloud.yandex.net/lockbox/v1/secrets"
    params = {"folderId": folder_id}
    headers = {"Authorization": f"Bearer {IAM_TOKEN}"}

    try:
        response = httpx.get(secrets_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        for secret in data.get("secrets", []):
            if secret_name in secret.get("currentVersion", {}).get("payloadEntryKeys", []):
                return secret["id"]

    except Exception as e:
        raise e

    return None


def get_secret(secret_name):
    secret_id = get_secret_id_by_name(secret_name, FOLDER_ID)

    if not secret_id:
        raise ValueError(f"Secret with name '{secret_name}' not found.")

    secret_payload_url = f"https://payload.lockbox.api.cloud.yandex.net/lockbox/v1/secrets/{secret_id}/payload"

    params = {}

    try:
        payload_response = httpx.get(
            secret_payload_url,
            headers={"Authorization": f"Bearer {IAM_TOKEN}"},
            params=params
        )
        payload_response.raise_for_status()
        payload_data = payload_response.json()

        secret_payload = {
            entry["key"]: (
                entry["textValue"] if "textValue" in entry else base64.b64decode(entry["binaryValue"]).decode())
            for entry in payload_data["entries"]
        }

        if secret_name in secret_payload:
            return secret_payload[secret_name]
        else:
            raise KeyError(f"Secret with name '{secret_name}' not found in the payload.")

    except Exception as e:
        raise e
