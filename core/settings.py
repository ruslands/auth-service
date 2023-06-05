# # Native # #
import os
import json
from typing import Literal, Optional

# # Installed # #
from fastapi_pagination import Page, Params
from pydantic import (
    BaseSettings,
    ValidationError,
    Extra,
    BaseModel,
    HttpUrl,
    PostgresDsn,
    root_validator,
)

# # Package # #
from core.aws import get_secret as get_secret_aws
from core.yc import get_secret as get_secret_yc
from core.yc import YCAuthMethod # noqa
from core.utils import jwk2pem
from core.logger import logger

__all__ = ("settings", "Params", "Page")

# pagination constraints #
Params.__fields__["size"].type_.le = 500


class SecretsSchema(BaseModel):
    PROJECT_NAME: str
    POSTGRES_URI: PostgresDsn
    HOSTNAME: str
    DEBUG: bool
    SENTRY_DSN: HttpUrl
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_URL: str
    KEYCLOAK_REALM: str
    APPLE_CLIENT_ID: str
    APPLE_TEAM_ID: str
    APPLE_KEY_ID: str
    APPLE_PRIVATE_KEY: str
    FACEBOOK_CLIENT_ID: str
    FACEBOOK_CLIENT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    JWK: str
    ENVIRONMENT: Literal["development", "staging", "production"]

    @root_validator
    def extract_jwk(cls, values):
        keys = jwk2pem(json.loads(values["JWK"]))
        values["PEM_PUBLIC_KEY"] = keys["PEM_PUBLIC_KEY"]
        values["PEM_PRIVATE_KEY"] = keys["PEM_PRIVATE_KEY"]
        return values


class Settings(BaseSettings):
    AWS_SECRET_ARN: Optional[str]
    YC_SECRET_ID: Optional[str]
    YC_SERVICE_ACCOUNT_ID: Optional[str]
    YC_AUTHORIZED_KEY_ID: Optional[str]
    YC_PRIVATE_KEY: Optional[str]

    class Config(BaseSettings.Config):
        # env_prefix = "AWS_"
        # env_file = ".env"
        extra = Extra.allow

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # serverless read from environment
        if set(SecretsSchema.__fields__.keys()).issubset(dict(os.environ).keys()):
            secrets = dict(os.environ)

        elif self.AWS_SECRET_ARN:
            secrets = get_secret_aws(self.AWS_SECRET_ARN)

        elif (
            self.YC_SECRET_ID
            and self.YC_SERVICE_ACCOUNT_ID
            and self.YC_AUTHORIZED_KEY_ID
            and self.YC_PRIVATE_KEY
        ):
            logger.info("reading secrets from Yandex.Cloud")
            YC_AUTH_CREDENTIALS = {
                "id": self.YC_AUTHORIZED_KEY_ID,
                "service_account_id": self.YC_SERVICE_ACCOUNT_ID,
                "private_key": self.YC_PRIVATE_KEY.replace("\\n", "\n"),
            }
            secrets = get_secret_yc(
                self.YC_SECRET_ID, "YC_AUTH_BY_SERVICE_ACCOUNT_KEY", YC_AUTH_CREDENTIALS
            )

        else:
            raise ValueError("No secrets found")

        secrets = SecretsSchema.parse_obj(secrets).dict()
        for key, value in secrets.items():
            setattr(self, key, value)


try:
    settings = Settings()
    logger.debug(f"settings: {settings}")
except ValidationError as e:
    logger.error(f"settings fetch error: {e}")
