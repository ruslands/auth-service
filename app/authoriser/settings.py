# # Installed # #
from pydantic import BaseSettings, ValidationError, Extra

# # Package # #
from aws import get_secret
from utils import jwk2pem
from logger import logger

__all__ = (
    "settings",
)


class BaseSettings(BaseSettings):
    class Config:
        # env_file = ".env"
        extra = Extra.allow


class SecretsSettings(BaseSettings):

    JWT_AUTH_SECRETS_MANAGER_ARN: str
    LAMBDA_AUTHORIZER_SECRETS_MANAGER_ARN: str

    class Config(BaseSettings.Config):
        env_prefix = "AWS_"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in get_secret(self.LAMBDA_AUTHORIZER_SECRETS_MANAGER_ARN).items():
            setattr(self, key, value)
        for key, value in jwk2pem(get_secret(self.JWT_AUTH_SECRETS_MANAGER_ARN)["keys"][0]).items():
            setattr(self, key, value)


try:
    settings = SecretsSettings()
    # logger.debug(f"Settings: {settings}")
except ValidationError as e:
    logger.error(f'Settings init error: {e}')
