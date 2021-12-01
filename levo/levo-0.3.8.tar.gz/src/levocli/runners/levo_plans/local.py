import pathlib
from typing import Optional

from .models import Plan


def get_plan(plan_name: str, catalog: str, workspace_id: str) -> Optional[Plan]:
    _catalog = pathlib.Path(catalog)
    plan_dir = _catalog / plan_name
    if plan_dir.is_dir():
        # TODO: Read the manifest and get lrn from it.
        return Plan(lrn="", name=plan_name, catalog=_catalog, workspace_id=workspace_id)
    return None
