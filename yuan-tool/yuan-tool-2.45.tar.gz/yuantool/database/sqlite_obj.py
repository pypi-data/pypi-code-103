import sqlite3
import logging

logger = logging.getLogger(__name__)


class Sqlite(object):

    def __init__(self, db_path):
        self.db = sqlite3.connect(db_path)

    def __del__(self):
        self.db.close()

    def execute_sql(self, sql):
        try:
            with self.db as conn:
                return conn.execute(sql)
        except Exception as e:
            logger.error('sql执行出错\nSQL: {} ,错误原因 {}'.format(sql, e), exc_info=True)
            return False
