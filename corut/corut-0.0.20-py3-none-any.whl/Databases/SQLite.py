#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
It was developed to facilitate SQLite Database operations.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

import os
import sqlite3
from threading import Lock
from ..Decorators import try_except, calculate_time_processing
from ..Shell import print_error


class SQLite:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.lock = None
        self.db_path = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    @try_except
    def connect(self, path_db=None):
        self.db_path = path_db if path_db else self.db_path
        if self.db_path and self.connection is None:
            self.disconnect()
            self.connection = sqlite3.connect(self.db_path, timeout=180, check_same_thread=False)
            if os.path.exists(self.db_path):
                self.connection.execute('PRAGMA foreign_keys = ON;')
            self.cursor = self.connection.cursor()
            print(f'------------- SQLite Database Connection Successfully Connected.')
        self.lock = Lock()
        return self.connection

    @try_except
    def disconnect(self):
        if self.lock and self.lock.locked():
            self.lock.release()
        if self.connection:
            self.connection.commit()
            self.connection.close()
        self.connection = None
        self.cursor = None
        self.lock = None
        print(f'------------- SQLite Database Connection Has Been Successfully Closed.')

    @try_except
    @calculate_time_processing
    def execute_sql(
            self, command=None, param=None, reply=False, execute_script=False, commit_status=True
    ):
        data = []
        if self.connection is None or self.cursor is None:
            self.connect(self.db_path)
        try:
            self.lock.acquire(True)
            if execute_script:
                self.cursor.executescript(command)
            else:
                if param:
                    self.cursor.execute(command, param)
                else:
                    self.cursor.execute(command)
            if commit_status:
                self.connection.commit()
                # print(f'{self.cursor.rowcount} record(s) affected')
            if reply:
                result = self.cursor.fetchall()
                data = [list(i) if list(i).__len__() > 1 else i[0] for i in result]
        except sqlite3.Error as error:
            print_error(error, locals())
            self.disconnect()
        finally:
            if self.lock.locked():
                self.lock.release()
        return data
