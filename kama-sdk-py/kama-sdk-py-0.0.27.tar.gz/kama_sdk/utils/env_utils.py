import os
import sys

from k8kat.auth.kube_broker import broker

legal_envs = ['production', 'development', 'test']

def set_run_env(_run_env):
  if _run_env in legal_envs:
    os.environ['FLASK_ENV'] = _run_env
    os.environ['KAT_ENV'] = _run_env
  else:
    raise Exception(f"Bad environment '{_run_env}'")


def is_in_cluster() -> bool:
  return broker.is_in_cluster_auth()


def is_out_of_cluster() -> bool:
  return not is_in_cluster()


def is_shell() -> bool:
  return exec_mode() == 'shell'


def run_env() -> str:
  return os.environ.get('FLASK_ENV', 'production')


def is_prod() -> bool:
  return run_env() == 'production'


def is_dev() -> bool:
  return run_env() == 'development'


def is_in_cluster_dev():
  return is_dev() and broker.is_in_cluster_auth()


def is_local_dev_server():
  return not broker.is_in_cluster_auth()


def is_test() -> bool:
  return run_env() == 'test'


def is_ci() -> bool:
  return is_test() and os.environ.get('CI')


def is_ci_keep():
  return os.environ.get("CI") == 'keep'


def exec_mode() -> str:
  from_argv = sys.argv[1] if len(sys.argv) >= 2 else None
  return from_argv or 'server'

