# coding=utf-8
from __future__ import absolute_import, print_function

import argparse
import faulthandler
import os
import sys

from suanpan.app.base import APP
from suanpan.imports import imports


def run(component, *args, **kwargs):
    if isinstance(component, str):
        component = f"{component[:-3]}.app" if component.endswith(
            ".py") else component
        component = imports(component)
        if not isinstance(component, APP):
            try:
                return component(*args, **kwargs)
            except:
                return component()
    return component.start(*args, **kwargs)


def cli():
    sys.path.append(os.path.abspath(os.curdir))
    parser = argparse.ArgumentParser()
    parser.add_argument("component")
    _args, _rest = parser.parse_known_args()

    sys.argv = sys.argv[:1]
    return run(_args.component, *_rest)


if __name__ == "__main__":
    faulthandler.enable()
    cli()
