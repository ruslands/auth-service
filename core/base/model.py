from sqlalchemy import TIMESTAMP, Column, Integer, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID as UUID_PG
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
MaterializedViewBase = declarative_base()

__all__ = (
    "BaseUUIDModel",
    "BaseOutboxModel",
    "Base",
)


class BaseUUIDModel:

    id = Column(UUID_PG(as_uuid=True), primary_key=True, index=True, server_default=text("gen_random_uuid()"))
    updated_at = Column(TIMESTAMP, index=True, server_default=func.now(), onupdate=func.current_timestamp())
    created_at = Column(TIMESTAMP, index=True, server_default=func.now())
    updated_by = Column(UUID_PG(as_uuid=True), nullable=True)
    created_by = Column(UUID_PG(as_uuid=True), nullable=True)
    description = Column(String, nullable=True)
    changelog = Column(JSONB, nullable=True, server_default=text("'[]'::json"))  # list of dict

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True  # todo дабл чек нужно ли это, возможно маскируем проблему в схемах


class BaseOutboxModel:
    """Base model for outbox"""

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # TODO: возможно нужны будут эти поля
    # updated_at = Column(TIMESTAMP, index=True, server_default=func.now(), onupdate=func.current_timestamp())
    # is_done = Column(Boolean, default=False)


class BaseAnalyticsModel:
    """Base model for analytics schema.
    UUID using as primary key instead of integer is for compatibility with BaseUUIDModel"""

    id = Column(UUID_PG(as_uuid=True), primary_key=True, index=True, server_default=text("gen_random_uuid()"))
