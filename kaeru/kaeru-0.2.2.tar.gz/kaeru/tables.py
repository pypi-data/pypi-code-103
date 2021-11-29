import asyncio
from sqlalchemy import Table, String, Column
from sqlalchemy.types import JSON
from sqlalchemy.sql.expression import null
import kaeru.database

metadata = kaeru.database.metadata

AnswerTable = Table(
    "assignment_list",
    metadata,
    Column("date", String(32), nullable=False, primary_key=True),
    Column("assignment", JSON, nullable=False),
    Column("answers", JSON, nullable=False),
)

UserTable = Table(
    "users",
    metadata,
    Column("email", String(32), primary_key=True),
    Column("password", String(32), nullable=False),
)

async def setup():
    async with kaeru.database.engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

asyncio.run(setup())