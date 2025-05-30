import uuid
from functools import wraps
from typing import BinaryIO, Optional

from types_aiobotocore_s3 import S3Client

from core.logger import logger


__all__ = ("S3ClientWrapper",)


class S3ClientWrapper:
    def __init__(self, s3_client: S3Client):
        self.s3_client = s3_client

    @property
    def exceptions(self):
        return self.s3_client.exceptions

    @staticmethod
    def create_bucket_if_not_exist(fn):
        @wraps(fn)
        async def wrapper(self, bucket: str, **kwargs):
            try:
                return await fn(self, bucket=bucket, **kwargs)
            except self.s3_client.exceptions.NoSuchBucket as e:
                logger.debug(f"S3[create_bucket_if_not_exist] no bucket ({bucket}) exists - {e}")
                await self.create_bucket(bucket=bucket)

                return await fn(self, bucket=bucket, **kwargs)

        return wrapper

    @create_bucket_if_not_exist
    async def put_file(
        self, bucket: str, file: BinaryIO, filename: str, content_type: str, key: Optional[str] = None
    ) -> str:
        # Generate s3 key if not provided
        if not (s3_key := key):
            s3_key = str(uuid.uuid4())

        try:
            logger.debug(f"S3[put_file] assign key - {s3_key}")
            resp = await self.s3_client.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=file,
                Metadata={"filename": filename, "content_type": content_type},
                ContentType=content_type,
            )
            logger.debug(f"S3[put_file] response - {resp}")
        except Exception as e:
            logger.debug(f"S3[put_file] failed - {e}")
            raise e
        return s3_key

    @create_bucket_if_not_exist
    async def get_file(self, bucket: str, key: str) -> dict:
        return await self.s3_client.get_object(Bucket=bucket, Key=key)

    @create_bucket_if_not_exist
    async def delete_file(self, bucket: str, key: str) -> dict:
        response = await self.s3_client.delete_object(Bucket=bucket, Key=key)
        logger.debug(f"S3[delete_file] response - {response}")

        return response

    async def create_bucket(self, bucket: str) -> dict:
        response = await self.s3_client.create_bucket(Bucket=bucket)
        logger.debug(f"S3[create_bucket] response - {response}")

        return response
