# # Native # #
import os
import json

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
    AUTH_SECRETS: str

    class Config(BaseSettings.Config):
        # env_prefix = "AWS_"
        # env_file = ".env"
        extra = Extra.allow

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in get_secret_aws(self.AUTH_SECRETS).items():
            if key == "JWK":
                value = jwk2pem(json.loads(value))
                for k, v in value.items():
                    setattr(self, k, v)
            setattr(self, key, value)
        self.ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(self.ACCESS_TOKEN_EXPIRE_MINUTES)
        self.REFRESH_TOKEN_EXPIRE_MINUTES = int(self.REFRESH_TOKEN_EXPIRE_MINUTES)
        self.REFRESH_TOKEN_TIMEOUT_MINUTES = int(self.REFRESH_TOKEN_TIMEOUT_MINUTES)


try:
    settings = SecretsSettings()
    logger.debug(f"Settings: {settings}")
except ValidationError as e:
    logger.error(f'Settings init error: {e}')
