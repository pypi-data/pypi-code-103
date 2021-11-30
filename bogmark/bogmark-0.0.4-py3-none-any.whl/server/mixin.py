import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class ConfigMixin(BaseModel):
    class Config:
        orm_mode = True
        use_enum_values = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps
