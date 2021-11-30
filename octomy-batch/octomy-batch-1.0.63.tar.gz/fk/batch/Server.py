from fk.batch.BatchProcessor import BatchProcessor
from multiprocessing import Process, connection
import os
import logging

logger = logging.getLogger(__name__)


class Server:
    def __init__(self, config):
        self.config = config

    def verify(self):
        batch_processor = BatchProcessor(config=self.config)
        return batch_processor.verify()

    def wrapper(self, num):
        logger.info(f"Batch worker {num} started with id:{os.getpid()}, parent:{os.getppid()}")
        batch_processor = BatchProcessor(config=self.config)
        while True:
            # Do some work
            batch_processor.process()

    def start(self, num):
        logger.info(f"Batch worker {num} starting...")
        worker = Process(target=self.wrapper, args=(num,))
        self.workers.append(worker)
        worker.start()
        return worker

    # Start server and serve forever
    def run(self):
        self.workers = []
        workers_count = self.config.get("batch-workers", 1)
        logger.info(f"Starting {workers_count} workers")
        num = 0
        for _ in range(workers_count):
            self.start(num)
            num += 1
        # Restart workes that terminate for whatever reason (they will self terminate on errors)
        while True:
            connection.wait(worker.sentinel for worker in self.workers)
            for worker in self.workers:
                logger.info(f"Batch worker terminating...")
                worker.join()
                self.workers.remove(worker)
                logger.info(f"Batch worker terminated")
                self.start(num)
                num += 1
