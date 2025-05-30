from abc import abstractmethod

from redis import from_url as sync_from_url
from redis.asyncio import from_url as async_from_url

from core.settings import settings


class _BaseRedisClient:
    URI = settings.REDIS_URI
    redis = None

    @abstractmethod
    def hset_str_keys(self, key, mapping):
        pass

    def __getattr__(self, name):
        return getattr(self.redis, name)


class _RedisClient(_BaseRedisClient):

    def __init__(self):
        self.redis = sync_from_url(self.URI, decode_responses=True)

    def hset_str_keys(self, key, mapping):
        str_keys = {str(key): value or "" for key, value in mapping.items() if key is not None}
        self.redis.hset(key, mapping=str_keys)

    def __getattr__(self, name):
        return getattr(self.redis, name)


class _AsyncRedisClient(_BaseRedisClient):

    def __init__(self):
        self.redis = async_from_url(self.URI, decode_responses=True)

    async def hset_str_keys(self, key, mapping):
        str_keys = {str(key): value or "" for key, value in mapping.items() if key is not None}
        await self.redis.hset(key, mapping=str_keys)

    def __getattr__(self, name):
        return getattr(self.redis, name)


RedisClient = _RedisClient()
AsyncRedisClient = _AsyncRedisClient()
