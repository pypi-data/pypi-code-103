import traceback
from datetime import datetime
from logging import getLogger, Handler

from sqlalchemy.engine.create import create_engine
from sqlalchemy.orm.session import Session, sessionmaker

logger = getLogger(__name__)


class DatabaseHandler(Handler):
    engine = None
    db_table = f"app_model_logs"
    container = None

    session_maker = None

    def __init__(self, level=0):
        super().__init__(level)

    @classmethod
    def init_db_adapter(cls, container, db_info):
        cls.container = container
        # logger 는 별로의 코드를 사용하여 DB 연결
        db_link = f'postgresql://{db_info["user"]}:{db_info["password"]}' \
                  f'@{db_info["host"]}:{db_info["port"]}/{db_info["database"]}'
        cls.engine = create_engine(db_link)
        cls.session_maker = sessionmaker(bind=cls.engine)

        create_table_sql = f"CREATE TABLE IF NOT EXISTS {cls.db_table}(" \
                           "id           serial  primary key      not null," \
                           "container    varchar(50)              not null," \
                           "process      integer                  not null," \
                           "process_name varchar(50)              not null," \
                           "thread_name  varchar(50)              not null," \
                           "name         varchar(50)              not null," \
                           "thread       bigint                   not null," \
                           "pathname     varchar(200)             not null," \
                           "func_name    varchar(50)              not null," \
                           "lineno       integer                  not null," \
                           "levelname    varchar(50)              not null," \
                           "time         timestamp with time zone not null," \
                           "message      text                     not null," \
                           "exc_info     text                     not null," \
                           "exc_text     text                     not null," \
                           "stack_info   text                     not null," \
                           "levelno      integer                  not null" \
                           ");"
        cls.execute_sql(create_table_sql)

    def __del__(self):
        # db 연결 제거
        try:
            if self.container is not None:
                self.engine.dispose()
        except Exception:
            traceback.print_exc()
        else:
            self.engine = None

    @classmethod
    def execute_sql(cls, sql: str):
        """
        sql문 단순 실행
        :param sql:
        :return:
        """
        session = cls.session_maker()
        try:
            session.execute(sql)
            session.commit()
        except Exception as e:
            session.rollback()
            traceback.print_exc()
            raise e
        finally:
            session.close()

    def emit(self, record):
        self.format(record)
        if record.exc_info is not None:
            # trackback 객체는 별로도 str화
            record.exc_info = ''.join(traceback.format_exception(*record.exc_info))

        # 메세지 특수문자 처리 - ''2개 붙이면 1개 처리됨
        record.message = record.message.replace('\'', '\'\'')

        insert_sql = f"INSERT INTO {self.db_table} (" \
                     f"container, process, process_name, " \
                     f"thread, thread_name, " \
                     f"name, pathname, func_name, lineno, " \
                     f"levelno, levelname, time, " \
                     f"message, exc_info, exc_text, stack_info" \
                     f") VALUES (" \
                     f"'{self.container}', '{record.process}', '{record.process}', " \
                     f"'{record.thread}', '{record.threadName}', " \
                     f"'{record.name}', '{record.pathname}', '{record.funcName}', '{record.lineno}', " \
                     f"'{record.levelno}', '{record.levelname}', '{datetime.now()}', " \
                     f"'{record.message}', '{record.exc_info}', '{record.exc_text}', '{record.stack_info}'" \
                     f");"
        self.execute_sql(insert_sql)
