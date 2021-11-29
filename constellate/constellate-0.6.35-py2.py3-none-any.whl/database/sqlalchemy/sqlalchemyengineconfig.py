import attr as attr
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine


@attr.s(kw_only=True, auto_attribs=True)
class _EngineConfig:
    # scheme contain the database type name and optionally a driver name. Eg: postgresql+psyops2
    connection_uri: str = None
    # scheme only contain the database type name
    connection_uri_plain: str = None
    # scheme only contain the database type name + schema name
    connection_uri_plain_schema: str = None
    # (Async) Engine is public engine for apps
    engine: AsyncEngine = None
    # Sync Engine is private engine for vertical/horizontal sharding needs only
    sync_engine: Engine = None
