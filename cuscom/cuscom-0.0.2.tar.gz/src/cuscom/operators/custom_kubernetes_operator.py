import json
import logging
from typing import Any, Dict, List, Optional

from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator
from airflow.hooks.base_hook import BaseHook
from airflow.models import Variable

from cuscom.utils import flatten_dict

log = logging.getLogger(__name__)


def on_failure(connection=None, msg_template=None):
    connection = connection or BaseHook.get_connection("slack")
    slack_msg_template = msg_template or Variable.get("SLACK_MESSAGE_TEMPLATE", "")

    def fn(context: Dict[str, Any]):
        arguments = {
            "task_id": "slack_task",
            "http_conn_id": "slack",
            "webhook_token": connection.password,
            "message": slack_msg_template.format_map(flatten_dict(context)),
            "username": "airflow",
            "channel": connection.login,
        }

        dag_run = context.get("dag_run")
        if hasattr(dag_run, "conf"):
            arguments["attachments"] = [{"text": json.dumps(dag_run.conf)}]

        failed_alert = SlackWebhookOperator(**arguments)
        return failed_alert.execute(context=context)

    return fn


class CustomKubernetesPodOperator(KubernetesPodOperator):
    def __init__(self, on_failure_callback=on_failure(), **kwargs):
        self._static_arguments = None
        self.conf = None
        kwargs["on_failure_callback"] = on_failure_callback
        super().__init__(**kwargs)

    def execute(self, context: Dict[str, Any]) -> Optional[str]:
        dag_run = context.get("dag_run")
        if hasattr(dag_run, "conf"):
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
        arguments = []
        for (key, value) in self.conf.items():
            arguments += ["--{}".format(key), str(value)]
        return arguments

    @arguments.setter
    def arguments(self, value):
        self._static_arguments = value
