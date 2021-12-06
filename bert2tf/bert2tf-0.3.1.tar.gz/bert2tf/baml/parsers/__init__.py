from typing import Type

from .base import YAMLParser
from .. import BAMLCompatible


def _get_all_parser(cls: Type['BAMLCompatible']):
    """Get all parsers and legacy parser of a class

    :param cls: target class
    :return: legacy parser
    """
    from ...executors import BaseExecutor
    from ...flow import Flow
    from ...drivers import BaseDriver

    if issubclass(cls, Flow):
        return _get_flow_parser()
    elif issubclass(cls, BaseExecutor):
        return _get_exec_parser()
    elif issubclass(cls, BaseDriver):
        return _get_driver_parser()


def _get_flow_parser():
    from .flow.legacy import LegacyParser

    return LegacyParser


def _get_exec_parser():
    from .executor.legacy import LegacyParser

    return LegacyParser


def _get_driver_parser():
    from .driver.legacy import LegacyParser

    return LegacyParser


def get_parser(cls: Type['BAMLCompatible']) -> 'YAMLParser':
    """


    .. # noqa: DAR401
    :param cls: the target class to parse
    :return: parser given the YAML version
    """
    return _get_all_parser(cls)()
