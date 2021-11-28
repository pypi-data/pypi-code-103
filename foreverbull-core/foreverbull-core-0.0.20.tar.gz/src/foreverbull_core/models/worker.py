from typing import List, NamedTuple, Optional

from foreverbull_core.models.base import Base


class Database(Base):
    user: str
    password: str
    netloc: str
    port: int
    dbname: str


class Parameter(Base):
    key: str
    value: Optional[int]
    default: int


class Instance(Base):
    session_id: str
    database: Optional[Database]
    parameters: Optional[List[Parameter]]


class Config(Base):
    id: Optional[str]
    service_id: Optional[str]
    name: str
    parameters: Optional[List[Parameter]]


class Run(NamedTuple):
    broker_url: str = ""
    local_host: str = ""


class BacktestRun(Run):
    service_id: str = ""
    instance_id: str = ""


class TestRun(NamedTuple):
    broker_url: str = ""
    local_host: str = ""
    backtest_id: str = ""
