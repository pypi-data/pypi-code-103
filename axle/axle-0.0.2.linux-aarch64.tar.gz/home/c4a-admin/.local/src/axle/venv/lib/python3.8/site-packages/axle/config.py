import yaml
import os
import pkg_resources
import pathlib

def default_config():
    getpath = lambda filename: str(pathlib.Path(pkg_resources.resource_filename(__name__, filename)).resolve())

    return {
        "flask": {
            "template_folder": getpath("templates"),
            "static_folder": getpath("static")
        },
        "jinja2": {
            "trim_blocks": True,
            "lstrip_blocks": True
        }
    }

def load_config(path = None):
    if path is None:
        path = os.getenv('PWMOOSE_CONFIG_PATH')

    if path is None:
        path = pkg_resources.resource_filename(__name__, "config.yml")

    config = default_config()
    with open(path, 'r') as fin:
        config.update(yaml.safe_load(fin.read()))

    return config
