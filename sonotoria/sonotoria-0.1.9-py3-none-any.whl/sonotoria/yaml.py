# -*- coding: utf-8 -*-
from typing import Any
from collections.abc import Callable
import yaml

from .jinja import template_string

def load(
    path: str,
    filters: dict[str, Callable[[Any], Any]]  = None,
    tests:   dict[str, Callable[[Any], bool]] = None,
    types:   dict[str, object]                = None,
    context: dict[str, Any]                   = None
) -> Any:
    """This function reads the file at the given path, templates it using jinja2 then returns the yaml data.

    Args:
        path: The path of the yaml file.
        filters: A dict with filters to add to the template engine. Names as keys, functions as values.
        tests: A dict of tests to add to the template engine. Names as keys, functions as values.
        types: A dict of objects to add to the template engine. Yaml tags as keys, objects as values.
        context: A dict with additional value for the context used when loading the yaml.

    Returns:
        The data contained in the templated yaml. Most probably a dict.

    Examples:
       >>> from sonotoria import yaml
       >>> data = yaml.load('my_file.yml')
    """
    with open(path, encoding='utf-8') as file:
        lines = file.read()
    return loads(lines, filters, tests, types, context)

def loads(
    yaml_content: str,
    filters: dict[str, Callable[[Any], Any]]  = None,
    tests:   dict[str, Callable[[Any], bool]] = None,
    types:   dict[str, object]                = None,
    context: dict[str, Any]                   = None
) -> Any:
    """This function reads the file at the given path, templates it using jinja2 then returns the yaml data.

    Args:
        yaml_content: The yaml as a string.
        filters: A dict with filters to add to the template engine. Names as keys, functions as values.
        tests: A dict of tests to add to the template engine. Names as keys, functions as values.
        types: A dict of objects to add to the template engine. Yaml tags as keys, objects as values.
        context: A dict with additional value for the context used when loading the yaml.

    Returns:
        The data contained in the templated yaml. Most probably a dict.

    Examples:
       >>> from sonotoria import yaml
       >>> yaml.loads('---\nparam: value\nparam2: {{ param }}')
       {'param': 'value', 'param2': 'value'}
    """
    for tag, type_ in (types or {}).items():
        _add_data_type(tag, type_)

    current_context = {}

    content = []
    for line in yaml_content.split('\n'):
        if '{{' not in line:
            content.append(line)
        else:
            current_context = yaml.safe_load('\n'.join(content))
            content.append(
                template_string(
                    line,
                    merge_context(current_context, context),
                    filters = filters or {},
                    tests = tests or {}
                )
            )

    return yaml.safe_load('\n'.join(content))

def merge_context(context1, context2):
    if isinstance(context1, dict) and isinstance(context2, dict):
        return context1 | context2
    if isinstance(context2, dict) and context1 is None:
        return context2
    return context1

class MyDumper(yaml.Dumper): #pylint: disable=too-many-ancestors
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)

def dumps(data):
    return yaml.dump(data, Dumper=MyDumper, default_flow_style=False)

def dump(file, data):
    with open(file, encoding='utf-8', mode='w') as fd:
        fd.write(dumps(data))

def ordered(class_):
    yaml.add_representer(class_, _represent_ordered)
    return class_

def constructed(class_):
    yaml.SafeLoader.add_constructor(class_.yaml_tag, class_.construct)


def _represent_ordered(dumper, data):
    return yaml.nodes.MappingNode(
        data.yaml_tag,
        [
            (
                dumper.represent_data(key),
                dumper.represent_data(getattr(data, key))
            )
            for key in data.attr_order
        ]
    )

def _add_data_type(tag, class_):
    class_.yaml_tag = f'!{tag}'
    try:
        constructed(class_)
    except AttributeError:
        class_.yaml_loader = yaml.SafeLoader
        new_class = type(f'Yaml{class_.__name__}', (yaml.YAMLObject,), {k: v for k, v in class_.__dict__.items() if not k.startswith('__')})
        if hasattr(new_class, 'attr_order'):
            ordered(new_class)
