import logging
from fk.batch.Server import Server
from fk.batch.BatchProcessor import BatchProcessor

logger = logging.getLogger(__name__)


def test_true():
    logger.info("Dummy unit test")
    return True


def test_server():
    config = {}
    server = Server(config)
    server.run()
    return True


def test_batch_processor():
    config = {}
    bp = BatchProcessor(config)
    return True
