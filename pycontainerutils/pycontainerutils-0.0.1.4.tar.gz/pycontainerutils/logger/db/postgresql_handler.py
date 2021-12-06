from datetime import datetime

import psycopg2


class PostgreSQLHandler:

    def __init__(self, db_table, container, db_info):
        self.db_table = db_table
        self.container = container
        # DB 연결
        self.db = psycopg2.connect(
            host=db_info["host"],
            dbname=db_info["database"],
            user=db_info["user"],
            password=db_info["password"],
            port=db_info["port"]
        )
        self.cursor = self.db.cursor()

        # 테이블 생성
        self.create_table()

    def __del__(self):
        self.db.close()
        self.cursor.close()

    def create_table(self):
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {self.db_table}(" \
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
        self.cursor.execute(create_table_sql)
        self.db.commit()

    def insert_data(self, record):
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
        self.cursor.execute(insert_sql)
        self.db.commit()
