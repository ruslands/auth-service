# # Native # #

# # Installed # #
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
# from async_lru import alru_cache
from sqlalchemy.engine import make_url
from sqlmodel import SQLModel

# # Package # #
from core.settings import settings


__all__ = (
    "async_engine",
    "init_database",
    "get_engine_url",
)

# cache = alru_cache(maxsize=None)


def get_engine_url():
    return make_url(settings.POSTGRES_URI)


async_engine = create_async_engine(
    url=get_engine_url(),
    echo=False,
    future=True,
    poolclass=NullPool,
    connect_args={'timeout': 5}
)

async def init_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    ...