import traceback
from datetime import datetime
from logging import getLogger, Handler

from pycontainerutils.logger.db.postgresql_handler import PostgreSQLHandler

logger = getLogger(__name__)


class DatabaseHandler(Handler):
    DBHandler = None
    container = None
    db_table = f"app_model_logs"

    def __init__(self, level=0):
        super().__init__(level)

    @classmethod
    def init_db_adapter(cls, container, db_info, db_type):
        cls.container = container
        if db_type == 'postgresql':
            cls.DBHandler = PostgreSQLHandler(db_table=cls.db_table, container=container, db_info=db_info)
        else:
            raise SyntaxError(f"db_type: {db_type}는 정의되지 않은 DB 타입입니다.")

    def emit(self, record):
        self.format(record)
        if record.exc_info is not None:
            # trackback 객체는 별로도 str화
            record.exc_info = ''.join(traceback.format_exception(*record.exc_info))

        # 메세지 특수문자 처리 - ''2개 붙이면 1개 처리됨
        record.message = record.message.replace('\'', '\'\'')
        # 저장
        self.DBHandler.insert_data(record)
