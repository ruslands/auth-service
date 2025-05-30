import json
import os
from typing import Literal
from urllib.parse import urljoin

from dotenv import dotenv_values
from fastapi_pagination import Page, Params
from integration.yandex import get_secret
from pydantic import (
    AnyHttpUrl,
    BaseModel,
    BaseSettings,
    Extra,
    HttpUrl,
    PostgresDsn,
    ValidationError,
    root_validator,
    validator,
)

from core.logger import logger
from core.utils import decode_base64, jwk2pem


__all__ = ("settings", "Params", "Page")

# Set pagination constraint for size
Params.__fields__["size"].type_.le = 500


EnvType = Literal["development", "staging", "production", "localhost", "testing"]


class Configuration(BaseModel):
    """Configuration from local .env file"""

    PROJECT_NAME: str
    DEBUG: bool
    REDIRECT_PATH: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    SENTRY_ENABLED: bool
    SENTRY_DSN: HttpUrl
    GOOGLE_CLIENT_ID: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_URL: str
    KEYCLOAK_REALM: str
    YANDEX_S3_ENDPOINT: str
    YANDEX_S3_BUCKET_NAME: str
    YANDEX_S3_REGION_NAME: str
    REDIS_TTL: int
    JWK: str  # Stored as base64, will be converted to PEM
    PEM_PUBLIC_KEY: str = None
    PEM_PRIVATE_KEY: str = None

    class Config(BaseSettings.Config):
        extra = "ignore"
        env_file = ".env"
        env_file_encoding = "utf-8"

    @root_validator(pre=False)
    def prepare_jwk(cls, values):
        """Convert JWK from base64 to PEM format and add to values"""
        try:
            decoded = decode_base64(values["JWK"])
            pem_keys = jwk2pem(decoded)
            values.update(
                {"PEM_PUBLIC_KEY": pem_keys.get("PEM_PUBLIC_KEY"), "PEM_PRIVATE_KEY": pem_keys.get("PEM_PRIVATE_KEY")}
            )
        except Exception as e:
            logger.error(f"Failed to convert JWK to PEM: {e}")
            raise ValueError(f"JWK conversion failed: {e}")
        return values

    @classmethod
    def load_from_env_file(cls, env_path: str = ".env"):
        """Load and validate configuration from .env file, then set environment variables"""
        # Resolve the env file path
        env_path = os.path.abspath(env_path)
        if not os.path.exists(env_path):
            logger.error(f".env file not found at {env_path}")
            raise FileNotFoundError(f".env file not found at {env_path}")

        # Load .env file into a dictionary for validation
        logger.debug(f"Parsing .env file at: {env_path}")
        dotenv_dict = dotenv_values(env_path)

        # Validate the configuration using Pydantic
        try:
            config = cls(**dotenv_dict)
            logger.debug("Configuration validated successfully")
            logger.debug(f"Configuration: {config.json(indent=2)}")
        except Exception as e:
            logger.error(f"Invalid configuration in .env file: {e}")
            raise ValueError(f"Invalid configuration in .env file: {e}")

        # Set validated configuration to environment variables
        cls._set_env_vars(config)

        return config

    @staticmethod
    def _set_env_vars(config: "Configuration"):
        """Set validated configuration values as environment variables"""
        for field_name, value in config.dict().items():
            if value is not None:
                os.environ[field_name] = str(value)


class Secret(BaseModel):
    ENVIRONMENT: EnvType
    URL: AnyHttpUrl
    AIRFLOW: dict
    FTP: dict
    NEXTCLOUD: dict
    REDIS_URI: str
    POSTGRES_URI: PostgresDsn
    KEYCLOAK_CLIENT_SECRET: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_SERVICE_ACCOUNT_CREDENTIALS: dict
    YANDEX_S3_ACCESS_KEY_ID: str
    YANDEX_S3_ACCESS_KEY: str

    class Config(BaseSettings.Config):
        extra = "ignore"

    @validator("AIRFLOW", "FTP", "NEXTCLOUD", "GOOGLE_SERVICE_ACCOUNT_CREDENTIALS", pre=True)
    def parse_dict(cls, value):
        if isinstance(value, str):
            # Convert string to dict, replacing single quotes with double quotes for JSON compatibility
            return json.loads(value.replace("'", '"'))
        return value

    @classmethod
    def check_env(cls) -> bool:
        """Validate environment variables"""
        # Get required fields
        required_fields = {
            field_name for field_name, field in cls.__fields__.items() if field.required and field.default is None
        }

        # Check for missing required configurations
        env_vars = set(os.environ.keys())
        missing_fields = required_fields - env_vars

        return False if missing_fields else True

    @classmethod
    def load_secrets_from_secret_manager(cls):
        """Load secrets from Yandex Cloud"""
        YANDEX_SECRET_ID = os.getenv("YANDEX_SECRET_ID")
        YANDEX_SERVICE_ACCOUNT_ID = os.getenv("YANDEX_SERVICE_ACCOUNT_ID")
        YANDEX_AUTHORIZED_KEY_ID = os.getenv("YANDEX_AUTHORIZED_KEY_ID")
        YANDEX_PRIVATE_KEY_BASE64 = os.getenv("YANDEX_PRIVATE_KEY_BASE64")

        if any(
            x is None
            for x in [YANDEX_SECRET_ID, YANDEX_SERVICE_ACCOUNT_ID, YANDEX_AUTHORIZED_KEY_ID, YANDEX_PRIVATE_KEY_BASE64]
        ):
            logger.error("Missing Yandex Cloud credentials")
            raise ValueError("All Yandex Cloud credentials must be provided")

        try:
            YANDEX_PRIVATE_KEY = decode_base64(YANDEX_PRIVATE_KEY_BASE64)
        except Exception as e:
            logger.error(f"Failed to decode YANDEX_PRIVATE_KEY_BASE64: {e}")
            raise ValueError(f"Failed to decode YANDEX_PRIVATE_KEY_BASE64: {e}")

        if not all([YANDEX_SECRET_ID, YANDEX_SERVICE_ACCOUNT_ID, YANDEX_AUTHORIZED_KEY_ID, YANDEX_PRIVATE_KEY]):
            logger.error("Missing Yandex Cloud credentials")
            raise ValueError("All Yandex Cloud credentials must be provided")

        logger.debug("Loading secrets from Yandex Cloud")
        yc_auth_credentials = {
            "id": YANDEX_AUTHORIZED_KEY_ID,
            "service_account_id": YANDEX_SERVICE_ACCOUNT_ID,
            "private_key": YANDEX_PRIVATE_KEY,
        }

        try:
            secrets_data = get_secret(
                secret_id=YANDEX_SECRET_ID, auth_type="YC_AUTH_BY_SERVICE_ACCOUNT_KEY", credentials=yc_auth_credentials
            )

            # Validate required fields
            required_fields = {
                field_name
                for field_name, field in Secret.__fields__.items()
                if field.required and field.default is None
            }
            missing_fields = required_fields - set(secrets_data.keys())

            if missing_fields:
                error_msg = f"Missing required secrets: {missing_fields}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # load to environment
            for key, value in secrets_data.items():
                os.environ[key] = value
            logger.debug(f"Secrets loaded from Yandex Cloud: {secrets_data}")

        except Exception as e:
            logger.error(f"Failed to load secrets from Yandex Cloud: {e}")
            raise


class Settings(BaseModel):
    ...

    class Config(BaseSettings.Config):
        extra = Extra.allow

    @property
    def BUCKET(self) -> str:
        """Return the Yandex S3 bucket name based on environment."""
        return f"{self.ENVIRONMENT}-{self.YANDEX_S3_BUCKET_NAME}"

    @property
    def MEDIA_BUCKET(self) -> str:
        """Return the media Yandex S3 bucket name based on environment."""
        return f"media-{self.ENVIRONMENT}-{self.YANDEX_S3_BUCKET_NAME}"

    @property
    def token_url(self) -> str:
        """Return the token URL for OAuth2PasswordBearer."""
        if not hasattr(self, "URL"):
            raise AttributeError("URL is not set.")
        return urljoin(self.URL, "/api/v1/auth/basic")


try:
    env_path = os.path.join(os.getcwd(), ".env")
    Configuration.load_from_env_file(env_path)
    if not Secret.check_env():
        Secret.load_secrets_from_secret_manager()

    c = Configuration.parse_obj(os.environ)
    s = Secret.parse_obj(os.environ)

    settings = Settings()

    for key, value in c.dict().items():
        setattr(settings, key, value)
    for key, value in s.dict().items():
        setattr(settings, key, value)
except ValidationError as e:
    logger.error(f"settings: {e}")
