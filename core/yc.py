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

OAUTH_TOKEN = "<OAuth-token>"
FOLDER_ID = "folder_id"


def get_iam_token(oauth_token):
    iam_url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    headers = {"Content-Type": "application/json"}
    data = {"yandexPassportOauthToken": oauth_token}

    try:
        response = httpx.post(iam_url, headers=headers, json=data)
        response.raise_for_status()
        iam_data = response.json()
        return iam_data["iamToken"]
    except Exception as e:
        raise e


def get_secret_id_by_name(secret_name, folder_id, IAM_TOKEN):
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
    IAM_TOKEN = get_iam_token(OAUTH_TOKEN)
    secret_id = get_secret_id_by_name(secret_name, FOLDER_ID, IAM_TOKEN)

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
