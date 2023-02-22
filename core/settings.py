# # Native # #
import os
import json
from typing import Literal

# # Installed # #
from fastapi_pagination import Page, Params
from pydantic import BaseSettings, ValidationError, Extra

# # Package # #
from core.aws import get_secret as get_secret_aws
from core.yc import get_secret as get_secret_yc
from core.utils import jwk2pem
from core.logger import logger

__all__ = (
    "settings",
    "Params",
    "Page"
)

# pagination constraints #
Params.__fields__["size"].type_.le = 500


class SecretsSettings(BaseSettings):
    SECRETS: str
    SECRETS_PROVIDER: Literal['aws', 'yandex']

    class Config(BaseSettings.Config):
        # env_prefix = "AWS_"
        # env_file = ".env"
        extra = Extra.allow

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
        if self.SECRETS_PROVIDER == 'yandex':
            secrets = get_secret_yc(self.SECRETS)
        elif self.SECRETS_PROVIDER == 'aws':
            secrets = get_secret_aws(self.SECRETS)
        for key, value in secrets.items():
            if key == "JWK":
                value = jwk2pem(json.loads(value))
                for k, v in value.items():
                    setattr(self, k, v)
            if key in ["ACCESS_TOKEN_EXPIRE_MINUTES", "REFRESH_TOKEN_EXPIRE_MINUTES", "REFRESH_TOKEN_TIMEOUT_MINUTES"]:
                value = int(value)
            setattr(self, key, value)


try:
    settings = SecretsSettings()
    logger.debug(f"settings: {settings}")
except ValidationError as e:
    logger.error(f'settings fetch error: {e}')
