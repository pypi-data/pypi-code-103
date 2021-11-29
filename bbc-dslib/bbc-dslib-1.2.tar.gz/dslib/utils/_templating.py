import os
from typing import Optional

from jinja2 import Environment, FileSystemLoader, StrictUndefined


def render_file(filepath: str, params: Optional[dict] = None, **kwargs) -> str:
    """
    Render a jinja template file. Includes and imports root is set to the directory component of ``filepath``.
    :param filepath: The path to the template file
    :param params: The parameters to bind to the template
    :param kwargs: The other parameters to bind to the template
    :return: The rendered template
    :raise: jinja2.UndefinedError if a parameter is undefined
    """
    folder = os.path.dirname(filepath)
    filepath = os.path.basename(filepath)
    params = params or {}
    environment = Environment(loader=FileSystemLoader(folder), undefined=StrictUndefined)
    return environment.get_template(filepath).render(params, **kwargs)


def render_string(string: str, params: Optional[dict] = None, **kwargs) -> str:
    """
    Render a jinja template string.
    :param string: The template string
    :param params: The parameters to bind to the template
    :param kwargs: The other parameters to bind to the template
    :return: The rendered template
    :raise: jinja2.UndefinedError if a parameter is undefined
    """
    params = params or {}
    environment = Environment(undefined=StrictUndefined)
    return environment.from_string(string).render(params, **kwargs)
