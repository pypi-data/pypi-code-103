import json

import yaml
from pydantic import BaseModel

from kntgen.str_helpers import *


@auto_str
class Param(BaseModel):
    name: str = None
    type_name: str = None
    default_value: str = None


@auto_str
class Unit(BaseModel):
    name: str = None
    params: list[Param] = []


@auto_str
class Event(Unit):
    need_check_connection: bool = False
    emit: list[str] = []


@auto_str
class State(Unit):
    is_error: bool = False


@auto_str
class Bloc(BaseModel):
    name: str = None
    need_singleton: bool = False
    need_cloud: bool = False
    need_custom_error: bool = False
    events: list[Event] = []
    states: list[State] = []

    @classmethod
    def from_json(cls, json_str: str):
        json_model = json.loads(json_str)
        return cls(**json_model)

    @classmethod
    def from_yaml(cls, yaml_stream):
        yaml_model = yaml.safe_load(yaml_stream)
        return cls(**yaml_model)

    @property
    def bloc_name_snake_case(self):
        return to_snake_case(self.name)
