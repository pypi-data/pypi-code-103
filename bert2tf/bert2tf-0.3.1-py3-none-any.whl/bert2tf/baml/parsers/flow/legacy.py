from typing import Dict, Type

from ..base import YAMLParser
from ....flow import Flow


class LegacyParser(YAMLParser):
    """The legacy parser."""

    def parse(self, cls: Type['Flow'], data: Dict) -> 'Flow':
        """
        :param cls: target class type to parse into, must be a :class:`BAMLCompatible` type
        :param data: flow yaml file loaded as python dict
        :return: the Flow YAML parser given the syntax version number
        """
        obj = super().parse(cls, data)

        # build pods
        for pod_attr in data.get('pods', []):
            needs = pod_attr.pop('needs', None)
            obj.add(needs=needs, **pod_attr)

        if 'gateway' in data.keys():
            obj.add_gateway(**data.get('gateway'))

        return obj
