import os

from mlflow.entities import SourceType
from mlflow.tracking.context.abstract_context import RunContextProvider
from mlflow.utils.mlflow_tags import MLFLOW_SOURCE_NAME, MLFLOW_SOURCE_TYPE, MLFLOW_USER


def _get_user():
    return os.environ.get("JUPYTERHUB_USER", default="unknown")


class KozaiNotebookRunContext(RunContextProvider):
    def __init__(self) -> None:
        self._cache = {}

    def in_context(self):
        return True

    def tags(self):
        return {
            MLFLOW_USER: _get_user(),
            MLFLOW_SOURCE_NAME: "Kozai Notebook",
            MLFLOW_SOURCE_TYPE: SourceType.to_string(SourceType.NOTEBOOK),
        }
