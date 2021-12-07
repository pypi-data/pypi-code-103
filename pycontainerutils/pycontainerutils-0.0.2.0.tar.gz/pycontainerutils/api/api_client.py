import time
from json.decoder import JSONDecodeError

import requests
import logging
import xmltodict
import json
logger = logging.getLogger(__name__)


class API_Client:
    timeout_seconds = 60
    waiting_time = 10
    waiting_count = 10
    total_count = 0

    def call_requests_repeat(self, url):
        response = None
        count = 0
        while count < self.waiting_count:
            count += 1
            self.total_count += 1
            try:    # 실질 api 요청
                response = requests.get(url, timeout=self.timeout_seconds)
                response.raise_for_status()
                return response.json()
            # 해당 오류가 발생시 무한 재시도 - 에러메세지 발생
            except requests.exceptions.ReadTimeout:
                logger.error(f"타임 아웃 재시도 {count} {url}")
            except requests.exceptions.ConnectionError:
                logger.error(f"요청 실패 재시도 {count} {url}")
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTPError 상태 코드 오류 \n"
                             f"{e}\n"
                             f"{type(e)}")
            # json이 아니라 xml로 오는 경우 dict로 인코딩을 하여 전달
            except JSONDecodeError as e:
                logger.error(f"JSONDecodeError 오류 - {e}")
                # xml 2 dict
                dict_type = xmltodict.parse(response.text)
                json_type = json.dumps(dict_type)
                dict2_type = json.loads(json_type)
                return dict2_type

            except Exception as e:
                # profiler.print_stats()
                logger.error(f"api 요청중 예상치 못한 오류 발생\n"
                             # f"{response.text}\n"
                             f"{response.headers}\n"
                             f"{e}\n"
                             f"{type(e)}")
            # 다시 api 호출시 대기 시간
            time.sleep(self.waiting_time)
