import unittest
from logging import getLogger

from pycontainerutils.db.BaseDB_Adapter import BaseDBAdapter
from pycontainerutils.db.DB_Adapter import DBAdapter
from pycontainerutils.db.df_utils import DBAdapterDF
from pycontainerutils.logger.setting_logger import Log_settings

Log_settings.logger_settings(
    logger_config={
        "": {
            "level": "DEBUG",
            "handlers": ["db", "console"],
        },
        "__main__": {
            "level": "INFO",
            "handlers": ["console"],
        },
        "sqlalchemy": {
            "level": "DEBUG",
            "handlers": [],
            "propagate": False
        },
        "selenium": {
            "level": "DEBUG",
            "handlers": [],
            "propagate": False
        },
        "urllib3": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False
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

BaseDBAdapter.init_settings(
    databases={
        'test': {
            "database": 'pycontainerutils',
            "user": 'pycontainerutils',
            "password": 'pycontainerutils',
            "host": "127.0.0.1",
            "port": 12345,
        },
    },
    default_db_name="test",
    is_echo_sql=False
)
logger = getLogger(__name__)


class LoggerAndDBAdapterTest(unittest.TestCase):
    test_table = f"test_table"
    # table sql
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {test_table} (" \
                       f" id     serial not null    primary key, " \
                       f" val_int   integer, " \
                       f" val_real   real," \
                       f" val_str varchar(50)" \
                       f");"
    delete_table_sql = f"DROP TABLE {test_table}"
    # test data
    test_sample_data = [123, 0.3, 'test str 1']
    # data sql
    insert_sql = f"INSERT INTO {test_table} (val_int, val_real, val_str)" \
                 f"VALUES ({test_sample_data[0]}, {test_sample_data[1]}, '{test_sample_data[2]}');"
    select_sql = f"SELECT * FROM {test_table}"
    delete_sql = f"DELETE FROM {test_table}"


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

    def test_log_double(self):
        """
        sql문으로 간단한 crud가 동작하는지 확인
        djagno의 auth group table을 사용하여 테스트
        :return:
        """
        db = DBAdapterDF(name="test_log_double")

        logger.debug("hello debug")
        logger.info("hello info")
        logger.warning("hello warning")
        logger.error("hello error")
        pass

    def test_crud(self):
        """
        sql문으로 간단한 crud가 동작하는지 확인
        djagno의 auth group table을 사용하여 테스트
        :return:
        """

        db = DBAdapter(name="test_crud LoggerAndDBAdapterTest")
        db.execute_sql(self.create_table_sql)


        # insert
        db.execute_sql(self.insert_sql)
        # check data insert - 정상적으로 데이터가 추가되었는지 확인
        data = db.fetch_data_by_sql(self.select_sql)
        self.assertEqual(data, [(1, *self.test_sample_data)])

        # 데이터 삭제
        db.execute_sql(self.delete_sql)

        # 데이터 존재 확인 - 데이터가 없어야 함
        data = db.fetch_data_by_sql(self.select_sql)
        self.assertEqual(data, [])
        db.execute_sql(self.delete_table_sql)
