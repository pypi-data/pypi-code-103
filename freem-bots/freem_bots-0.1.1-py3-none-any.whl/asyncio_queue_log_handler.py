import logging
from asyncio import Queue
import sys


class AsyncioQueueLogHandler(logging.StreamHandler):
	def __init__(self, log_queue: Queue) -> None:
		super().__init__(stream = sys.stdout)
		self.log_queue: Queue = log_queue
		self.setFormatter(logging.Formatter('%(asctime)s|%(name)s|%(levelname)s: %(message)s'))

	def emit(self, record: logging.LogRecord):
		msg: str = self.format(record)
		self.log_queue.put_nowait(msg)
