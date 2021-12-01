import os

import typer

from gosu import cmds

app = typer.Typer()
app.add_typer(cmds.ci.app, name="ci")
app.add_typer(cmds.python.app, name="python")
app.add_typer(cmds.django.app, name="django")


def import_from_path(path, module_name):
    import importlib.util

    spec = importlib.util.spec_from_file_location(module_name, path)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    return foo


def find_local_gosu_cmds():
    cmds_path = os.getcwd() + "/cmds.py"
    if not os.path.isfile(cmds_path):
        return

    import_from_path(cmds_path, "gosu.user.cmds")


if __name__ == "gosu.main":
    find_local_gosu_cmds()
