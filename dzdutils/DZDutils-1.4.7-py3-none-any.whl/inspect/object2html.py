#!/usr/bin/python
import os
import tempfile
import webbrowser
import inspect
import json
from time import sleep


def retrieve_name(var):
    """
        Gets the name of var. Does it from the out most frame inner-wards.
        :param var: variable to get name from.
        :return: string
        """
    for fi in reversed(inspect.stack()):
        names = [
            var_name
            for var_name, var_val in fi.frame.f_locals.items()
            if var_val is var
        ]
        if len(names) > 0:
            return names[0]


def serialize(obj):
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "__dict__"):
        return {str(obj): obj.__dict__}
    return str(obj)


def var2json(var):
    return json.dumps(var, default=serialize)


def is_primitive(var):
    return isinstance(var, (bool, int, float, complex, str, bool,))


def instance2dict(var, show_private_attrs=False, show_callable_attrs=False, walk=False):
    dic = {}
    for attribute_name in dir(var):
        attribute = getattr(var, attribute_name)
        if (
            show_private_attrs and attribute_name.startswith("_")
        ) or not attribute_name.startswith("_"):
            if callable(attribute) and show_callable_attrs:
                dic[attribute_name] = "<Callable {}>".format(str(attribute))
            elif is_primitive(attribute):
                dic[attribute_name] = attribute
            elif walk:
                dic[attribute_name] = instance2dict(attribute)
    return dic


def object2html(var):
    name = retrieve_name(var)
    type_ = type(var).__name__
    data = var2json(var)
    templatedir = os.path.dirname(os.path.realpath(__file__))
    templatepath = os.path.join(templatedir, "html_template.html.template")
    with open(templatepath, "r") as file:
        html_template = "\n".join(file.readlines())
    html_file_tmp = tempfile.NamedTemporaryFile(delete=True)
    html_file_path = html_file_tmp.name + ".html"
    html_file = open(html_file_path, "w")
    html_file.write(
        html_template.replace("{{ DATA }}", data, 1)
        .replace("{{ TYPE }}", type_, 2)
        .replace("{{ NAME }}", name, 2)
    )
    html_file.close()
    webbrowser.open("file://" + html_file_path)
