"""
DB 와 연결하는 부분
"""
import io
from logging import getLogger

import pandas as pd

from pycontainerutils.db.DB_Adapter import DBAdapter

logger = getLogger(__name__)


class DBAdapterDF(DBAdapter):
    """
    데이터를 사용하는 엔진
    해당 데이터를 다루는 모든 조작을 담당
    """

    def check_delete_insert_df(self, table_name, df, primary_keys):
        """DB에 중복된 데이터는 모두 제거후 새 데이터 삽입
        :param table_name: 테이블명
        :param df: 새로 넣을 dataframe
        :param primary_keys: 중복확인시 비교할 값
        :return:
        """
        # 요약 정보 작성
        buf = io.StringIO()
        df.info(buf=buf)
        df_info_str = buf.getvalue()
        # 로그
        logger.debug(f"check_delete_insert_df data info {table_name}\n"
                     f"{df.head()}\n"
                     f"{df_info_str}")
        #
        for x, item in df.iterrows():
            # DB 데이터 삭제
            delete_sql = f"DELETE FROM {table_name}"
            delete_sql = self.make_sql_by_df_keys(item, delete_sql, primary_keys)
            self.execute_sql(delete_sql, level=5)

            # 데이터 삽입
            self.insert_dict(table_name, item.to_dict(), level=5)

    @staticmethod
    def make_sql_by_df_keys(data, init_sql, primary_keys):
        # DB 데이터 조회

        where_key_list = []
        for key in primary_keys:
            # 정수나 실수면 그냥 입력
            if type(data[key]) == int or type(data[key]) == float:
                where_key_list.append(f" {key} = {data[key]}")
            # 문자열인 경우 '' 추가
            else:
                where_key_list.append(f" {key} = '{data[key]}'")

        # list를 합쳐서 sql문 제작
        result_sql = init_sql + " WHERE " + ' AND'.join(where_key_list)
        return result_sql
