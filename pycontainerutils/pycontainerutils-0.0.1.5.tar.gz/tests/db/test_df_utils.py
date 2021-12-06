import unittest
from datetime import datetime, timedelta

from pandas.core.frame import DataFrame

from pycontainerutils.db.BaseDB_Adapter import BaseDBAdapter
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


class DBAdapterDFTest(unittest.TestCase):
    test_table = f"test_table"
    db = DBAdapterDF(name="test DBAdapterDFTest")
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
        self.db.execute_sql(self.create_table_sql)

        pass

    def tearDown(self):
        """
        테스트에 사용하는 데이터 삭제
        """
        self.db.execute_sql(self.delete_table_sql)

        pass

    def test_connect(self):
        """
        sql문으로 간단한 crud가 동작하는지 확인
        djagno의 auth group table을 사용하여 테스트
        :return:
        """
        db = DBAdapterDF(name="test_connect DBAdapterDFTest")
        db.execute_sql(self.select_sql)
        pass

    def test_crud(self):
        """
        sql문으로 간단한 crud가 동작하는지 확인
        djagno의 auth group table을 사용하여 테스트
        :return:
        """
        db = DBAdapterDF(name="test_crud DBAdapterDFTest")
        # insert
        db.execute_sql(self.insert_sql)
        # check data insert - 정상적으로 데이터가 추가되었는지 확인
        data = self.db.fetch_data_by_sql(self.select_sql)
        self.assertEqual(data, [(1, *self.test_sample_data)])

        # 데이터 삭제
        self.db.execute_sql(self.delete_sql)

        # 데이터 존재 확인 - 데이터가 없어야 함
        data = self.db.fetch_data_by_sql(self.select_sql)
        self.assertEqual(data, [])

    def test_check_delete_insert_df(self):
        db = DBAdapterDF(name="test_check_delete_insert_df DBAdapterDFTest")
        # 테이블 생성
        table_create_sql = f"CREATE TABLE IF NOT EXISTS test_df (" \
                           "str1                       varchar(50)      not null, " \
                           "str2                       varchar(50)      not null, " \
                           "time_start                    timestamp        not null, " \
                           "time_end                     timestamp        not null, " \
                           "val_int                   integer          not null, " \
                           "val_float double precision not null " \
                           ");"
        db.execute_sql(sql=table_create_sql)
        df = DataFrame(data={
            "str1": ["test1", "test2"],
            "str2": ["test10", "test22"],
            "time_start": [datetime(year=2020, month=1, day=1), datetime(year=2020, month=3, day=1)],
            "time_end": [datetime(year=2020, month=6, day=30), datetime(year=2020, month=7, day=10)],
            "val_int": [10, 4],
            "val_float": [10.3, 4.3],
        })
        print("-----------------")
        db.check_delete_insert_df(table_name="test_df", df=df, primary_keys=["str1", "str2", "time_start", "time_end"])
        print("-----------------")
        # 테이블 삭제
        table_delete_sql = f"DROP TABLE test_df"
        db.execute_sql(sql=table_delete_sql)

    def test_check_delete_insert_df_again(self):
        for i in range(5):
            self.test_check_delete_insert_df()
