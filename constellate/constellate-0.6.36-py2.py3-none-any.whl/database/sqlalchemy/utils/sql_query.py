from typing import Dict, Union

from sqlalchemy.engine import Engine
from sqlalchemy.engine.default import DefaultDialect
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.sql import Select, Executable


def stringify(
    query: Union[Select, Executable] = None,
    engine: Engine = None,
    dialect: DefaultDialect = None,
    compile_kwargs: Dict = {},
) -> str:
    """
    @query: Query object to get plain SQL query from
    @engine: Database type to know the SQL dialect to convert into

    src: https://stackoverflow.com/a/23835766/219728
    """
    return (
        query.compile(engine)
        if engine is not None
        else query.compile(
            dialect=dialect, compile_kwargs={"literal_binds": True, **compile_kwargs}
        )
    )


async def resolve_engine_from_query(
    session: AsyncSession = None, query: Union[Select, Executable] = None
) -> AsyncEngine:
    """
    Resovle the engine used by the query. Useful when the db session uses shards
    """
    # PERF: This will execute the query!!!! As of 2021 Mai, I did not find a way to get this info without executing the
    # query against the db
    _ignore_result = await session.execute(query)
    engine = _ignore_result.raw.connection.engine
    return engine
