import os
import pymysql
import pandas as pd
import fnmatch
import glob


class DbCommon(object):
    def get_maria_db_data(self, host, port, user, password, db, statement):
        local = dict(host=host,
                     port=port,
                     user=user,
                     password=password,
                     db=db)
        conn = pymysql.connect(**local)
        df_ora = pd.read_sql(statement, con=conn)
        conn.close()
        return df_ora

    def execute_maria_db_sql(self, host, port, user, password, db, statement):
        local = dict(host=host,
                     port=port,
                     user=user,
                     password=password,
                     db=db)
        conn = pymysql.connect(**local)
        cur = None
        if conn is not None:
            cur = conn.cursor()
        if cur is not None:
            sql = statement
            cur.execute(sql)
            conn.commit()
        conn.close()

    def execute_maria_db_sqls_from_folder(self, host, port, user, password, db, folder_path):
        local = dict(host=host,
                     port=port,
                     user=user,
                     password=password,
                     db=db)
        files = glob.glob(folder_path)
        conn = pymysql.connect(**local)
        with conn.cursor() as cursor:
            for file in files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        for row in f.readlines():
                            try:
                                cursor.execute(row)
                                conn.commit()
                            except Exception as e:
                                print(row)
                                print(f'{e}')
                except Exception as e:
                    print(f'{e}')

    def find_replace(self, directory, find, replace, file_pattern):
        for path, dirs, files in os.walk(os.path.abspath(directory)):
            for filename in fnmatch.filter(files, file_pattern):
                filepath = os.path.join(path, filename)
                with open(filepath, encoding='utf-8') as f:
                    s = f.read()
                s = s.replace(find, replace)
                with open(filepath, "w", encoding='utf-8') as f:
                    f.write(s)

    def init_db_data(self, db_conn_host, db_conn_port, db_conn_user, db_conn_password, db_conn_db):
        # print('start init_db_data')
        db_common = DbCommon()
        all_foreign_key_constraints = db_common.get_maria_db_data(host=db_conn_host,
                                                                  port=db_conn_port,
                                                                  user=db_conn_user,
                                                                  password=db_conn_password,
                                                                  db=db_conn_db,
                                                                  statement=f"""SELECT KCU.*
                                                                              FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE KCU
                                                                              JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS TC 
                                                                              ON (KCU.CONSTRAINT_NAME = TC.CONSTRAINT_NAME AND
                                                                                  KCU.TABLE_SCHEMA = TC.TABLE_SCHEMA)
                                                                              WHERE 1=1
                                                                              AND TC.CONSTRAINT_TYPE = 'FOREIGN KEY'
                                                                              AND TC.CONSTRAINT_SCHEMA = '{db_conn_db}'""")
        # region delete foreign key constraints
        # print('start delete foreign key constraints')
        # print(all_foreign_key_constraints)
        for index, row in all_foreign_key_constraints.iterrows():
            constraint_name = row['CONSTRAINT_NAME']
            table_schema = row['TABLE_SCHEMA']
            table_name = row['TABLE_NAME']
            # print(constraint_name)
            # print(table_schema)
            # print(table_name)
            db_common.execute_maria_db_sql(host=db_conn_host,
                                           port=db_conn_port,
                                           user=db_conn_user,
                                           password=db_conn_password,
                                           db=db_conn_db,
                                           statement=f"""ALTER TABLE {table_schema}.{table_name}
                                                         DROP FOREIGN KEY {constraint_name}""")
        # print('finish delete foreign key constraints')
        # endregion
        all_tables = db_common.get_maria_db_data(host=db_conn_host,
                                                 port=db_conn_port,
                                                 user=db_conn_user,
                                                 password=db_conn_password,
                                                 db=db_conn_db,
                                                 statement=f"""SELECT TABLE_NAME
                                                             FROM INFORMATION_SCHEMA.TABLES
                                                             WHERE TABLE_SCHEMA = '{db_conn_db}'
                                                             AND TABLE_NAME != 'alembic_version'""")
        # region truncate tables
        # print('start truncate tables')
        for index, row in all_tables.iterrows():
            table_name = row['TABLE_NAME']
            # print(table_name)
            db_common.execute_maria_db_sql(host=db_conn_host,
                                           port=db_conn_port,
                                           user=db_conn_user,
                                           password=db_conn_password,
                                           db=db_conn_db,
                                           statement=f"""TRUNCATE TABLE {db_conn_db}.{table_name}""")
        # print('finish truncate tables')
        # endregion
        # region insert data to db
        # print('start insert data to db')
        folder_path = os.path.join('tests', 'functions', 'db', 'sqls', '*')
        db_common.execute_maria_db_sqls_from_folder(host=db_conn_host,
                                                    port=db_conn_port,
                                                    user=db_conn_user,
                                                    password=db_conn_password,
                                                    db=db_conn_db,
                                                    folder_path=folder_path)

        # print('finish insert data to db')
        # endregion
        # region restore foreign key constraints
        # print('start restore foreign key constraints')
        for index, row in all_foreign_key_constraints.iterrows():
            constraint_name = row['CONSTRAINT_NAME']
            table_name = row['TABLE_NAME']
            column_name = row['COLUMN_NAME']
            main_table = row['REFERENCED_TABLE_NAME']
            main_table_column = row['REFERENCED_COLUMN_NAME']
            db_common.execute_maria_db_sql(host=db_conn_host,
                                           port=db_conn_port,
                                           user=db_conn_user,
                                           password=db_conn_password,
                                           db=db_conn_db,
                                           statement=f"""ALTER TABLE {db_conn_db}.{table_name}
                                          ADD FOREIGN KEY ({column_name}) REFERENCES {main_table} ({main_table_column})
                                          """)
        # print('finish restore foreign key constraints')
        # endregion
        # print('finish init_db_data')
