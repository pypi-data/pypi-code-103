import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("sqlite+aiosqlite:////Users/faith/kaeru.db", connect_args={"check_same_thread": False})
metadata = sa.MetaData()
