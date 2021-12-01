import os
from typing import Dict

import redis
from rq import Worker, Connection, Queue

from kama_sdk.cli import cli_helper
from kama_sdk.core.core import consts
from kama_sdk.utils.logging import lwar

redis_url = os.getenv('WORK_REDIS_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)


def get_meta() -> Dict:
  return {'name': MODE_NAME, 'info': 'Start the background worker'}


def register_arg_parser(_):
  pass


def run(options: Dict):
  cli_helper.start_engines()
  cli_helper.handle_ns(options, MODE_NAME, allow_empty=False)
  _start(consts.MAIN_WORKER, consts.TELEM_WORKER)


def start_telem():
  _start(consts.TELEM_WORKER)


def _start(*queue_names: str):
  with Connection(conn):
    worker = Worker(
      queues=queue_names,
      connection=conn
    )

    main_queue = Queue(consts.MAIN_WORKER, connection=conn)
    telem_queue = Queue(consts.TELEM_WORKER, connection=conn)

    main_removed = main_queue.empty()
    telem_removed = telem_queue.empty()

    if main_removed or telem_removed:
      detail = f"main({main_removed}) telem({telem_removed})"
      lwar(f"cleared zombie jobs in queues {detail}")

    worker.work()


MODE_NAME = "worker"
