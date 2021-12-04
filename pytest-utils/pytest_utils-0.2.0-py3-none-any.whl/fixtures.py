from datetime import datetime, timezone
from logging import DEBUG, basicConfig, getLogger

from pytest import fixture

__all__ = [
    'console_logger',
    'sample_datetime',
]


@fixture(scope='session')
def console_logger():
    """
    Test console logger.
    """
    basicConfig(format='%(asctime)-15s %(levelname)-5.5s %(message)s')
    logger = getLogger(__name__)
    logger.setLevel(DEBUG)
    return logger


@fixture()
def sample_datetime():
    return datetime(year=1970, month=1, day=1, tzinfo=timezone.utc)
