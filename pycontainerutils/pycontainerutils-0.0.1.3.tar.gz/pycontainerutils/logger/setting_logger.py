import json
import logging.config

from pycontainerutils.logger.base_logger_config import base_logger_config
from pycontainerutils.logger.db.DB_handler import DatabaseHandler


class Log_settings:
    log_config = None

    def initialize(self):
        logging.config.dictConfig(self.log_config)

    @classmethod
    def logger_settings(cls, logger_config, container_name, db_info=None, db_type="postgresql"):
        """로그 설정
        :param db_type: db 프로그램 종류
        :param db_info: 로그를 저장할 db
        :param container_name: db log에 들어갈 컨테이너 이름
        :param logger_config: logger 설정
        :return:
        """
        # db 연결정보 입력시 db handler 설정
        if db_info is not None:
            DatabaseHandler.init_db_adapter(container=container_name, db_info=db_info, db_type=db_type)
        # 기본 정의된 handler 사용
        cls.log_config = base_logger_config
        # logger만 입력받아서 사용
        cls.log_config['loggers'] = logger_config
        # 생성
        logging.config.dictConfig(cls.log_config)


def open_log_setting_py(log_config):
    logging.config.dictConfig(log_config.log_config)


def open_log_setting_json():
    """
    json 파일 형식으로 된 logger 설정파일을 읽어와 로거를 설정한다.
    :return:
    """
    with open('loggers.json') as f:
        config_json = json.load(f)
        print("로그 설정")
        # print(config)
        logging.config.dictConfig(config_json)
