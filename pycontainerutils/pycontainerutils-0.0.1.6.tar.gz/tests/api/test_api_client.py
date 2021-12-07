import unittest
from logging import getLogger

from pycontainerutils.api.api_client import API_Client
from pycontainerutils.logger.setting_logger import Log_settings

Log_settings.logger_settings(
    logger_config={
        "": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
        "test_logger_console": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
    },
    container_name="APIClientTest",
)

logger = getLogger(__name__)


class APIClientTest(unittest.TestCase):

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
        api = API_Client()
        url = f"http://apis.data.go.kr/1360000/NwpModelInfoService/getLdapsUnisAll?ServiceKey=5RR1UuzOEtgenAG4uusefJERqDYkVskem%2B%2FAEQez3aVQ%2BBMDc6iwlg6%2B%2BSVq3XoIwU%2BRg4GZS4r0PZJU1uBSJg%3D%3D&pageNo=1000&numOfRows=50000&dataType=JSON&leadHour=1&dataTypeCd=Temp&baseTime=202112050300"
        logger.debug(url)
        data = api.call_requests_repeat(url)
        if "response" in data:
            print(data)
        elif "OpenAPI_ServiceResponse" in data:
            print(data)
        pass
