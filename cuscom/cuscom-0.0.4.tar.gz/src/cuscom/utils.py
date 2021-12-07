import logging
from typing import Any, Dict

from airflow import settings
from airflow.models import DagRun
from sqlalchemy.exc import SQLAlchemyError

log = logging.getLogger(__name__)


def flatten_dict(nested_dict: Dict, sep=".") -> Dict[str, Any]:
    def items():
        for key, value in nested_dict.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    yield key + sep + subkey, subvalue
            else:
                yield key, value

    return dict(items())


def default_arguments_fn(conf):
    arguments = []
    for (key, value) in conf.items():
        arguments += [f"--{key}", str(value)]
    return arguments


def from_kebab_case_key(d):
    return {k.replace("-", "_"): v for (k, v) in d.items()}


def trigger_dag(dag_id, conf, run_id):
    # pylint: disable=unexpected-keyword-arg
    try:
        run = DagRun(dag_id=dag_id, conf=conf, run_id=run_id, external_trigger=True)
        session = settings.Session()
        session.add(run)
        log.info("Triggering run %s of dag %s", run_id, dag_id)
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        log.info("Failed to trigger DAG run %s of %s", run_id, dag_id)
    finally:
        session.close()
