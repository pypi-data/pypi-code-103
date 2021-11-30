from typing import Union, Callable, Dict

import pandas as pd
import regex
from constellate.database.sqlalchemy.session.multienginesession import MultiEngineSession
from constellate.database.sqlalchemy.utils.sql_query import resolve_engine_from_query
from pandas import DataFrame
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.future import Engine, Connection
from sqlalchemy.sql import Select


def _driverless_engine_url(engine: AsyncEngine = None):
    url = str(engine.url)
    # match foo+bar in foo+bar://something
    match_drivername = regex.match("^.+?(?=:\\/)", url)
    span = match_drivername.span()
    db_driver_protocol = url[span[0] : span[1]]
    parts = db_driver_protocol.split("+")

    driver_protocol = parts[1]
    url = url.replace(driver_protocol, "", 1).replace("+", "", 1)
    return url


async def read_sql(sql: str = None, engine: AsyncEngine = None) -> DataFrame:
    # As of June 2021: Pandas does not yet support SQLALchemy 2.x engine / AsyncEngine
    # So, transform the async engine url into a driver agnostic url for pandas
    # to connect to it directly
    url = _driverless_engine_url(engine=engine.url)
    df = pd.read_sql(sql, url)
    return df


async def read_sql2(
    session: Union[MultiEngineSession] = None,
    query: Select = None,
    params: Dict = None,
    find_async_engine: Callable[[Engine], AsyncEngine] = None,
    find_engine_url: Callable[[Engine], str] = None,
) -> DataFrame:
    limit_clause = query._limit_clause
    sync_engine = None
    async_engine = None
    sync_engine_url = None
    try:
        # Force database to compute the result but still return a valid empty result:w
        query.limit(0)
        # Resolve engine
        sync_engine = await resolve_engine_from_query(session=session, query=query)
        if find_async_engine is not None:
            async_engine = await find_async_engine(engine=sync_engine)
        elif find_engine_url is not None:
            async_engine_url = await find_engine_url(engine=sync_engine)
    finally:
        query._limit_clause = limit_clause

    if async_engine is None:
        raise NotImplementedError("not sure if this can be implemented with SQLAlchemy info only")

    sql = query

    params = params or {}

    if sync_engine_url is not None:
        return pd.read_sql(sql, sync_engine_url, params=params)
    elif async_engine is not None:
        async with async_engine.begin() as connection:

            def read_sql(connection: Connection) -> DataFrame:
                return pd.read_sql(sql, connection, params=params)

            return await connection.run_sync(read_sql)
