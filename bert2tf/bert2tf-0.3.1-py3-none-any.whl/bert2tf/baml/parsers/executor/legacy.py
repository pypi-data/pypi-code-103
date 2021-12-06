from typing import Dict, Type

from ..base import YAMLParser
from ...helper import parse_use_source
from ....executors import BaseExecutor


class LegacyParser(YAMLParser):
    """The legacy parser."""

    def parse(self, cls: Type['BaseExecutor'], data: Dict) -> 'BaseExecutor':
        """
        :param cls: target class type to parse into, must be a :class:`BAMLCompatible` type
        :param data: flow yaml file loaded as python dict
        :return: the executor YAML parser given the syntax version number
        """
        from ... import BAML

        # load drivers
        _requests = data.get('requests', {})
        for key, drivers in _requests.items():
            for idx, driver in enumerate(drivers):
                driver = BAML.load(parse_use_source(driver['use']))
                _requests[key][idx] = driver

        # load obj
        obj = cls(**data.get('use_with', {}), metas=data.get('metas', {}), requests=_requests)

        return obj
