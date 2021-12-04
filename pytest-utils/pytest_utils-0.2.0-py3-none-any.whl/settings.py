import os
from configparser import ConfigParser
from typing import Any, Dict, Mapping, Optional

from pytest import FixtureRequest

__all__ = [
    'read_settings',
]


def read_settings(
    request: FixtureRequest,
    section: str,
    defaults: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Read settings from ini file, that defined via "--ini" pytest
    commandline option.

    :param request: Fixture request.
    :param section: Name of ini section to read.
    :param defaults: Optional default settings values.
    :return: Dictionary of settings.
    """
    config_uri = os.path.abspath(request.config.option.ini)

    settings_defaults = {'here': os.path.dirname(config_uri)}
    settings_defaults.update(defaults or {})

    config_parser = ConfigParser(defaults=settings_defaults)
    config_parser.read(config_uri)

    settings = dict(config_parser.items(section))
    settings['__file__'] = config_uri
    return settings
