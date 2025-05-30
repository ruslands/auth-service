from enum import Enum
from typing import Any, Optional

from integration.postgres.database import job_async_engine
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession


async def get_distinct_model_values(
    conn: AsyncConnection | AsyncSession,
    model: Optional[str] = None,
    attribute: Optional[str] = None,
    schema: Optional[str] = "core",
    pk_name: Optional[str] = None,
    sql: Optional[str] = None,
) -> Optional[dict[Any, Any]]:
    if sql is None:
        if model is None and attribute is None:
            raise ValueError("Either sql or pair (model, attribute) must be provided")
    result = await conn.execute(
        text(
            sql
            if sql
            else "SELECT DISTINCT {schema}.{table}.{pk_name},  {schema}.{table}.{attribute} "
            "FROM {schema}.{table}".format(
                table=model, schema=schema, pk_name=pk_name if pk_name else attribute, attribute=attribute
            )
        )
    )
    attributes = result.fetchall()
    return {row[0]: row[1] for row in attributes}


class SQLAdv(Enum):
    fetchall = "fetchall"
    commit = "commit"


async def job_sql_executor(sql_query: str, adv: SQLAdv = None):
    async with job_async_engine.connect() as conn:  # todo в отдельную функцию
        request = await conn.execute(text(sql_query))
        if adv == SQLAdv.fetchall:
            results = request.fetchall()
        else:
            results = None
        if adv == SQLAdv.commit:
            await conn.commit()
    return results
