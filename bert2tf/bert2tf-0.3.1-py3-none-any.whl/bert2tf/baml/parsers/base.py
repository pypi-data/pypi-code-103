from typing import Dict, Union

if False:
    from ...executors import BaseExecutor
    from ...flow import Flow
    from ...drivers import BaseDriver


class YAMLParser:
    """Flow YAML parser for specific version

    Every :class:`YAMLParser` must implement two methods and one class attribute:
        - :meth:`parse`: to load data (in :class:`dict`) into a :class:`BaseFlow` or :class:`BaseExecutor` object
        - :meth:`dump`: to dump a :class:`BaseFlow` or :class:`BaseExecutor` object into a :class:`dict`
        - :attr:`version`: version number in :class:`str` in format ``MAJOR.[MINOR]``
    """

    def parse(self, cls: type, data: Dict) -> Union['Flow', 'BaseExecutor', 'BaseDriver']:
        """Return the Flow YAML parser given the syntax version number


        .. # noqa: DAR401
        :param cls: target class type to parse into, must be a :class:`BAMLCompatible` type
        :param data: flow yaml file loaded as python dict
        """

        obj = cls(**data.get('use_with', {}))

        return obj

