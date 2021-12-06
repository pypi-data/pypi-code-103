import importlib.abc
import importlib.util
import os
import sys
from typing import cast


def load_user_entrypoint(entrypoint: str) -> None:
    # We could use importlib.import_module but we want to guarantee entrypoint
    # is loaded with the correct module name. (e.g. main.py should be module main)
    # See jetpack.utils.qualified_name for how we generage job names
    # In particular, app/main.py should be module "main" and not "app.main"

    # We ensure the entrypoint path is in path so that imports work as expected.
    sys.path.append(os.path.dirname(entrypoint))
    module_name = os.path.basename(entrypoint).split(".")[0]
    spec = importlib.util.spec_from_file_location(module_name, entrypoint)
    assert spec is not None
    entrypoint_module = importlib.util.module_from_spec(spec)
    cast(importlib.abc.Loader, spec.loader).exec_module(entrypoint_module)
