from typing import Iterable

from core.cache.values import cache_registry


class _CacheManager:
    def __init__(self, data: Iterable["CachedValueBase"]):
        self.data = [x.__call__() for x in data]
        self.map: dict["CacheV2KV" | "CacheV2RowList", "CachedValueBase"] = {
            cached_value.name: cached_value for cached_value in self.data
        }

    async def get_multi(self, keys: Iterable["CacheV2"], connection):
        res = []
        # подумать про redis.pipeline
        for key in keys:
            value = await self.map[key].get(connection)
            res.append(value)
        return res

    def update_multi(self, keys: list[str] = None):
        """Принудительное обновление ключей."""
        # todo можно вынести отдельную ручку на это, но мб это и нужно если все будет работать как задумано.
        pass


CacheManager = _CacheManager(data=cache_registry)
