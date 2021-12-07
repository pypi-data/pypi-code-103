import logging
from typing import Any, Dict, List, Optional

from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from cuscom.hooks import slack
from cuscom.utils import default_arguments_fn


log = logging.getLogger(__name__)


class CustomKubernetesPodOperator(KubernetesPodOperator):
    def __init__(self, arguments_fn=default_arguments_fn, **kwargs):
        self._static_arguments = []
        self.conf = None
        self.arguments_fn = arguments_fn
        if "on_failure_callback" not in kwargs:
            kwargs["on_failure_callback"] = slack.on_failure()
        super().__init__(**kwargs)

    def execute(self, context: Dict[str, Any]) -> Optional[str]:
        dag_run = context.get("dag_run")
        if dag_run is not None and hasattr(dag_run, "conf"):
            self.conf = dag_run.conf

        log.info("Received conf: %s", self.conf)
        return super().execute(context)

    @property
    def arguments(self) -> List[str]:
        return self._static_arguments + self.dynamic_arguments

    @property
    def dynamic_arguments(self) -> List[str]:
        if self.conf is None:
            return []
        return self.arguments_fn(self.conf)

    @arguments.setter  # type: ignore
    def arguments(self, value):
        self._static_arguments = value
