# -*- coding: utf-8 -*-
"""
Simple database connector using sqlalchemy.

Peter Raso
Created on Fri Jun 18 12:35:32 2021
"""
import os
from sqlalchemy import create_engine, MetaData, Table, insert
from sqlalchemy.engine.url import URL


class BrtgDB:

    def __init__(self, database = 'brtg'):
        driver = 'mysql+pymysql'
        user = os.environ['DB_USER']
        pwd = os.environ['DB_PASS']
        host = os.environ['DB_HOST']
        port = os.environ['DB_PORT']
        self.url = URL.create(driver, user, pwd, host, port, database)
        self.engine = None
        self.conn = self.connect()

    def connect(self):
        self.engine = create_engine(self.url,
                               connect_args={'ssl': {'ssl_verify_cert': 'true'}},
                               encoding='utf-8')
        return self.engine.connect()

    def execute(self, query):
        return self.conn.execute(query)

    def add_table_connector(self, table_name, schema_name=None):
        metadata = MetaData(bind=None)
        table_connector = Table(table_name, metadata, schema=schema_name,
                                autoload=True, autoload_with=self.engine)
        return table_connector

    def log_test_results(self, test_run, status=0, details=None):
        # name of table to store test results
        table = self.add_table_connector('t_test_results')
        stmt = insert(table).values(test_run=test_run,
                                    status=status,
                                    details=details)
        self.conn.execute(stmt) 

    def log_change(self, job_name, table_name, event_type, details=None):
        # name of table to store changes
        table = self.add_table_connector('t_loading_logging')
        stmt = insert(table).values(job_name=job_name,
                                    table_name=table_name,
                                    event_type=event_type,
                                    details=details)
        self.conn.execute(stmt) 

    def log_data_error(self, table_name, id_table, column_name, value_old, value_new):
        table = self.add_table_connector('t_data_errors')
        stmt = insert(table).values(table_name=table_name,
                                    id_table=id_table,
                                    column_name=column_name,
                                    value_old=value_old,
                                    value_new=value_new)
        self.conn.execute(stmt) 

    def __del__(self):
        self.conn.close()

