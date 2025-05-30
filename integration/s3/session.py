from typing import AsyncGenerator

from aiobotocore.session import get_session
from integration.s3.s3 import S3ClientWrapper

from core.settings import settings


__all__ = ("get_s3_client",)


async def get_s3_client() -> AsyncGenerator[S3ClientWrapper, None]:
    s3_config = {
        "endpoint_url": settings.YANDEX_S3_ENDPOINT,
        "region_name": settings.YANDEX_S3_REGION_NAME,
        "aws_secret_access_key": settings.YANDEX_S3_ACCESS_KEY,
        "aws_access_key_id": settings.YANDEX_S3_ACCESS_KEY_ID,
    }

    # Create the S3 client session and yield the wrapper
    async with get_session().create_client("s3", **s3_config) as client:
        yield S3ClientWrapper(s3_client=client)
