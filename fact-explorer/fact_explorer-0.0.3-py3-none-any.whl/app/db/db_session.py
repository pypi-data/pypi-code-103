from datetime import datetime
from functools import wraps
import asyncpg
from json import dumps
from typing import Any, Callable, Dict, Optional
from fact_explorer.app.entities.fact import FactOut
from fact_explorer.config import get_configuration


class Database:
    def __init__(self) -> None:
        self.config = get_configuration()
        self._cursor = None

        self._connection_pool = None
        self.con = None

    def connect_wrapper(func: Callable) -> Callable:  # type: ignore
        @wraps(func)
        async def wrapped(self, *args, **kwargs):  # noqa: ANN
            if not self._connection_pool:
                await self.connect()
            else:
                self.con = await self._connection_pool.acquire()
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    print(e)
                finally:
                    await self._connection_pool.release(self.con)

        return wrapped

    async def connect(self) -> None:
        if not self._connection_pool:
            try:
                self._connection_pool = await asyncpg.create_pool(
                    min_size=1,
                    max_size=10,
                    command_timeout=60,
                    host=self.config.database_host,
                    port=self.config.database_port,
                    user=self.config.database_user,
                    password=self.config.database_password,
                    database=self.config.database_name,
                )

            except Exception as e:
                print(e)

    async def fetch_rows(self, query: str) -> Any:
        if not self._connection_pool:
            await self.connect()
        else:
            self.con = await self._connection_pool.acquire()
            try:
                result = await self.con.fetch(query)
                return result
            except Exception as e:
                print(e)
            finally:
                await self._connection_pool.release(self.con)

    @connect_wrapper
    async def fetch_by_example(
        self,
        *,
        header_example: Optional[Dict[str, str]] = None,
        payload_example: Optional[Dict[str, str]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Any:
        if not header_example:
            header_example = {}
        if not payload_example:
            payload_example = {}

        stmt = await self.con.prepare(  # type: ignore
            (
                "select *"
                " from fact"
                " where header @> cast($1 as jsonb)"
                " and payload @> cast ($2 as jsonb)"
                " order by ser desc"
                " limit $3::int"
                " offset $4::int"
            )
        )
        print(stmt.get_query())
        result = await stmt.fetch(
            dumps(header_example), dumps(payload_example), limit, offset
        )
        return result

    @connect_wrapper
    async def fetch_by_time(self, *, until: datetime) -> Any:
        """
        Will fetch the entries up to approximately until. Will fetch at least 50 rows
        iff available. Will fetch in batches afterwards. Since factcast does not have
        an index on _ts this is faster than a FTS although of course less than ideal
        """
        result = []
        async with self.con.transaction():  # type: ignore
            cursor = await self.con.cursor("select *" " from fact" " order by ser desc")  # type: ignore
            result += await cursor.fetch(50)
            last_retrieved_time = datetime.fromtimestamp(
                int(str(FactOut.parse_obj(result[-1]).header["meta"]["_ts"])[:10])  # type: ignore
            )
            while last_retrieved_time > until:
                # Doing this by fetching rows. it is way faster than a FTS.
                result += await cursor.fetch(50)
                last_retrieved_time = datetime.fromtimestamp(
                    int(str(FactOut.parse_obj(result[-1]).header["meta"]["_ts"])[:10])  # type: ignore
                )
            return result


db_instance = Database()
