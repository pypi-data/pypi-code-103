import json
from typing import Any, Dict, Optional

from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator
from airflow.models import Connection
from airflow.hooks.base_hook import BaseHook
from airflow.models import Variable

from cuscom.utils import flatten_dict
from cuscom.exceptions import CuscomException


def on_failure(connection: Optional[Connection] = None, msg_template: Optional[str] = None):
    connection = connection or BaseHook.get_connection("slack")
    slack_msg_template = msg_template or Variable.get("SLACK_MESSAGE_TEMPLATE", "")
    if connection is None:
        raise CuscomException("No slack connection configured")

    if slack_msg_template is None:
        raise CuscomException("No slack message template available")

    def fn(context: Dict[str, Any]):
        arguments = {
            "task_id": "slack_task",
            "http_conn_id": "slack",
            "webhook_token": connection.password,  # type: ignore
            "message": slack_msg_template.format_map(flatten_dict(context)),
            "username": "airflow",
            "channel": connection.login,  # type: ignore
        }

        dag_run = context.get("dag_run")
        if dag_run is not None and hasattr(dag_run, "conf"):
            arguments["attachments"] = [{"text": json.dumps(dag_run.conf)}]

        failed_alert = SlackWebhookOperator(**arguments)
        return failed_alert.execute(context=context)

    return fn
