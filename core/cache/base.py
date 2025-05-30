import typing

from integration.postgres.utils import get_distinct_model_values
from integration.redis.database import AsyncRedisClient
from pydantic import parse_obj_as
from sqlalchemy.ext.asyncio import AsyncSession

from core.logger import logger
from core.settings import settings


if typing.TYPE_CHECKING:
    from core.cache.values import CacheV2KV

KEYS_FORMAT = "cached:{}"


class CachedValueBase:
    """На первом этапе работает только со словарями, т.е везде redis.hget а не redis.get"""

    # query = None
    name: "CacheV2KV" = None  # значение для вставки в шаблон "cached:{name}", ссылка на реестр кеша
    get_distinct_model_args: dict = None
    client = AsyncRedisClient
    ttl = settings.REDIS_TTL  # seconds

    def __init__(self):
        if self.name is None:
            raise NotImplementedError(f"Cache name is not defined {self.__class__.__name__}")
        self._key = KEYS_FORMAT.format(self.name.name)

    async def get(self, connection: AsyncSession):
        """если уже в кеше берем из него, ttl не обновляем, если в кеше нет, берем из sql"""
        value = await self._read_cache()
        if value:  # кеш из пустого словаря запрещены
            value = await self._load(value)
            return value
        value = await self._read_sql(connection)
        formatted = await self._format_value(value)
        dump = await self._dump(formatted)

        await self._write_cache(dump)

        return value

    async def _read_cache(self):
        value = await self.client.hgetall(self._key)
        return value

    async def _read_sql(self, connection: AsyncSession):
        value = await get_distinct_model_values(connection, **self.get_distinct_model_args)
        return value

    async def _write_cache(self, value):
        if not value:
            logger.error(f"Skip empty cache: {self._key}")
            return
        await self.client.hset_str_keys(self._key, mapping=value)
        await self.client.expire(self._key, time=self.ttl)

    async def _format_value(self, value):
        """Фильтрация из sql запроса"""
        return value

    async def _dump(self, value):
        """Если не соответствует типам redis json.dumps"""
        return value

    async def _load(self, value):
        """Если не соответствует типам python json.dumps"""
        return value


class CachedValueListOrm(CachedValueBase):
    query = None
    schema = None

    async def _read_sql(self, connection: AsyncSession):
        res = await connection.execute(self.query)
        return res.fetchall()

    async def _read_cache(self):
        value = await self.client.get(self._key)
        return value

    async def _write_cache(self, value):
        #  todo возможно рейзить пустые значения по аналогии со словарями,
        #   или прописать кейсы когда пустая запись валидна
        # if not value:
        #     logger.error(f"Skip empty cache: {self._key}")
        await self.client.set(self._key, value, ex=self.ttl)

    async def _dump(self, value):
        """Если не соответствует типам redis json.dumps
        orm -> pydantic schema -> json"""
        pass
        pydantic_schema = parse_obj_as(self.schema, value)

        return pydantic_schema.json()

    async def _load(self, value):
        """Если не соответствует типам python json.dumps"""
        return self.schema.parse_raw(value).__root__
