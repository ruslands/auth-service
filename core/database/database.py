# # Native # #

# # Installed # #
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import QueuePool
# from async_lru import alru_cache
from sqlalchemy.engine import make_url
from sqlmodel import SQLModel

# # Package # #
from core.settings import settings
from core.logger import logger


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
    # pool_size=20,
    # max_overflow=0
    poolclass=QueuePool
)


async def init_database():
    logger.info("init database")
    async with async_engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

# Here, we're using QueuePool as the connection pool class,
# which manages a queue of connections to the database. When you execute a query,
# it will automatically take a connection from the pool, execute the query,
# and return the connection to the pool. This helps ensure that only one operation
# is executed on a given connection at a time, which should help avoid the error you're seeing.
