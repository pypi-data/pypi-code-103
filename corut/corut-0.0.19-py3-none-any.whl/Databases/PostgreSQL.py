#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
It was developed to facilitate PostgreSQL Database operations.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

from pg import DB
from ..Decorators import try_except, calculate_time_processing


class PostgreSQL:
    def __init__(self):
        self.connection = None
        self.config = {}

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    @try_except
    def connect(self):
        assert isinstance(self.config, dict), 'Please Enter Connection Parameters.'
        if self.connection is None:
            self.connection = DB(**self.config)
            print(f'------------- PostgreSQL Database Connection Successfully Connected.')
        return self.connection

    @try_except
    def disconnect(self):
        if self.connection:
            self.connection.close()
        self.connection = None
        print(f'------------- PostgreSQL Database Connection Has Been Successfully Closed.')

    @try_except
    @calculate_time_processing
    def execute_sql(self, query=None, reply=False):
        data = []
        if self.connection is None:
            self.connect()
        result = self.connection.query(query)
        if reply:
            data = [list(i) if list(i).__len__() > 1 else i[0] for i in result.getresult()]
        return data
