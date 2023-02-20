# # Native # #
from typing import AsyncGenerator

# # Installed # #
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_scoped_session
# from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel.ext.asyncio.session import AsyncSession

# # Package # #
from app.database.database import async_engine

__all__ = (
    "get_session",
    "get_session_with_bind"
)


async_session_factory = sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False
)

async_session_factory = async_scoped_session(async_session_factory, scopefunc=lambda: None)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        # yield session
        # await session.commit()
        # await session.close()
        try:
            yield session
            await session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            await session.close()


async def get_session_with_bind() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory(bind=async_engine) as session:
        yield session


async def get_session_with_bind_and_autocommit() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory(bind=async_engine, autocommit=True) as session:
        yield session


async def get_session_with_bind_and_autoflush() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory(bind=async_engine, autoflush=True) as session:
        yield session


async def get_session_with_bind_and_autocommit_and_autoflush() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory(bind=async_engine, autocommit=True, autoflush=True) as session:
        yield session
