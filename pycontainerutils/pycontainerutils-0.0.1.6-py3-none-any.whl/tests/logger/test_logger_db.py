import unittest
from logging import getLogger

from pycontainerutils.logger.setting_logger import Log_settings

Log_settings.logger_settings(
    logger_config={
        "": {
            "level": "DEBUG",
            "handlers": ["console", "db"],
        },
    },
    container_name="LoggerDBTest",
    db_info={
        "database": 'pycontainerutils',
        "user": 'pycontainerutils',
        "password": 'pycontainerutils',
        "host": "127.0.0.1",
        "port": 12345,
    },
)

logger = getLogger(__name__)


class LoggerDBTest(unittest.TestCase):

    def setUp(self):
        """
        테스트에 사용하는 데이터 삭제
        """
        pass

    def tearDown(self):
        """
        테스트에 사용하는 데이터 삭제
        """
        pass

    def test_connect(self):
        """
        sql문으로 간단한 crud가 동작하는지 확인
        djagno의 auth group table을 사용하여 테스트
        :return:
        """
        logger.debug("hello debug")
        logger.info("hello info")
        logger.warning("hello warning")
        logger.error("hello error")
        pass
