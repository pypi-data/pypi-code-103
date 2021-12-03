"""
Module for interacting with an SQLite3 database (.db files)
"""
import csv
import sqlite3
import pathlib
import logging
import time
import threading
from queue import Queue

from abc import ABC, abstractmethod
from typing import List, Tuple, Union, Dict
from contextlib import closing
from datetime import datetime, timedelta

import warnings


logger = logging.getLogger(__name__)


class MissingColumnError(Exception):
    """
    Error for a missing column in a DatabaseTable
    """

    def __init__(self, msg=None):
        self.msg = msg or 'An expected column is missing from the database table'

    def __str__(self):
        return self.msg


def get_db_table_names(file_path: str) -> List[str]:
    """Return a list of table names, given the database path"""
    with sqlite3.connect(file_path) as db:
        with closing(db.cursor()) as cur:
            cur.execute(f"SELECT name FROM sqlite_master WHERE type='table'")
            table_names = [names[0] for names in cur.fetchall()]
    return table_names


def get_db_column_names(file_path, table_name: str) -> List[str]:
    """Return a list of the column names for a table in a database, given the database path"""
    raise NotImplementedError('access the get_table_column_names method of DatabaseTable')


class DatabaseManager:
    _instances: List['DatabaseManager'] = []

    CYCLE_TIME: float = 0.05

    def __init__(self, target_file: str):
        """
        Database manager with insertion queue to avoid locked file issues

        :param target_file: target database file
        """
        self.target_file = target_file
        self._kill_flag = False
        self.thread = threading.Thread(
            target=self.insert_runner,
            name='DI database thread',
            daemon=True,
        )
        # queue expects an insert query and any arguments passed as the second variable
        self.queue: Queue = Queue()
        self.thread.start()
        DatabaseManager._instances.append(self)

    def insert_runner(self):
        """Threading target for performing inserts into the database"""
        logger.info('starting database insertion thread')
        with sqlite3.connect(self.target_file, uri=True) as db:
            while self._kill_flag is False:
                with closing(db.cursor()) as cur:
                    while self.queue.empty() is False:
                        insert_query, values = self.queue.get()
                        cur.execute(insert_query, values)
                    db.commit()
                time.sleep(self.CYCLE_TIME)
        logger.info(f'database insertion thread terminating')

    def stop_insertion_runner(self):
        """killswitch for the insertion runner"""
        self._kill_flag = True
        DatabaseManager._instances.remove(self)

    @classmethod
    def get_database_manager(cls, file_path: str) -> 'DatabaseManager':
        """
        Retrieves a database manager instance for the provided file path. If an instance already exists for that
        file path, the instance will be returned. Otherwise a new one will be created.

        :param file_path: file path to write to
        """
        for inst in cls._instances:
            if inst.target_file == file_path:
                return inst
        return cls(file_path)

    @classmethod
    def stop_all_instances(cls):
        """stops all database insertion instance threads"""
        for inst in cls._instances:
            inst.stop_insertion_runner()


class DatabaseTable(ABC):
    def __init__(self, file_path: Union[str, pathlib.Path]):
        """
        Create a SQLite3 table at the database at the path with the columns if it doesnt already exist

        This is a SQLite3 database table mixin. To use, subclass this class and define the table_name and
        column_name_types. Basic sql injection attack prevention is provided by disallowing the user to set the
        table name and column definitions (defined when the class is defined). There is no protection against imporper
        definition of the subclasses.

        :param file_path: path to the database (.db file)
        """
        file_path = pathlib.Path(file_path).absolute()
        self.database_manager = DatabaseManager.get_database_manager(str(file_path.absolute()))

        self._file_path: pathlib.Path = None
        self.file_path = file_path

        # create table if it does not exist
        commands = []
        # build command and parameters so that they can be executed safely
        for name, value_type in self.column_name_types:
            commands.append(f'{name} {value_type}')
        table_structure = ', '.join(commands)
        with sqlite3.connect(str(self.file_path.absolute())) as db:
            with closing(db.cursor()) as cur:
                # create the table
                cur.execute(
                    f'CREATE TABLE IF NOT EXISTS {self.table_name} ({table_structure})',
                )
            db.commit()

        self.column_names: List[str] = self.get_table_column_names()

    @property
    def file_path(self) -> pathlib.Path:
        """Path to the database .db file"""
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        if value is not None:
            if isinstance(value, pathlib.Path) is False:
                value = pathlib.Path(value)
            if value.suffix != '.db':
                value = value.parent / (value.name + '.db')
            self._file_path = value

    @property
    def _csv_path(self) -> pathlib.Path:
        """default path to save the contents of the table from the .db file to a csv file"""
        return self.file_path.with_name(self.file_path.name[:-3] + f' - {self.table_name}.csv')

    @property
    @abstractmethod
    def table_name(self) -> str:
        """Name of the table in the database"""
        raise NotImplementedError

    @property
    @abstractmethod
    def column_name_types(self) -> List[Tuple[str, str]]:
        """defines the column names and types to be used if the table needs to be created"""
        raise NotImplementedError

    @property
    def _base_query(self) -> str:
        """the base query for the instance. This provides a basic security layer between the user and the query for
        avoiding sql injections"""
        warnings.warn('use _select_query instead', DeprecationWarning, stacklevel=2)
        return self._select_query

    @property
    def _select_query(self) -> str:
        """the select query for the instance. This provides a basic security layer between the user and the query for
        avoiding sql injections"""
        return f'select * from {self.table_name}'

    @property
    def _insert_query(self) -> str:
        """the delete query for the instance. This provides a basic security layer between the user and the
        query for avoiding sql injections"""
        return f'insert into {self.table_name} values ({", ".join(["?" for _ in range(len(self.column_names))])})'

    @property
    def _delete_query(self) -> str:
        """the base query for the instance. This provides a basic security layer between the user and the query for
        avoiding sql injections"""
        # todo should it be that this must be implemented in the subclass to for safety?
        return f'delete from {self.table_name}'

    @property
    def db_table_names(self) -> List[str]:
        """A list of the name of all tables in the database"""
        names = get_db_table_names(file_path=str(self.file_path.absolute()))
        return names

    def get_table_column_names(self) -> List[str]:
        """Return a list of the column names for a table in a database, given the database path"""
        with sqlite3.connect(str(self.file_path.absolute())) as db:
            with closing(db.cursor()) as cur:
                # todo scrub for sql injection
                cur.execute(self._select_query)
                column_names = [description[0] for description in cur.description]
        return column_names

    def retrieve(self) -> List[List]:
        """
        Retrieve all entries for the table in the database

        :return: a list of lists. the inner lists each represent a row from the database, and each value in the inner
            list represents the value for a column index
        """

        with sqlite3.connect(str(self.file_path.absolute())) as db:
            with closing(db.cursor()) as cur:
                cur.execute(self._select_query)
                rows = cur.fetchall()
        out = []
        # iterate through each row retrieved from the query
        for row in rows:
            # add the row to the output
            out.append([*row])
            # # need to typecast values?
            # # a list of the column types
            # column_types = [self.column_name_types[column_index][1].lower() for column_index in range(len(self.column_names))]
            # for column_index, value in enumerate(row):
            #     column_type = column_types[column_index]
            #     # typecast needed here?
        return out

    def insert(self, *record: Union[Tuple, List[Tuple]]) -> None:
        """
        Inserts values into the database table. The order of the values in the Tuple must match to how they are
        listed in the column_name_types property

        :param record: tuple or list of tuples. each tuple represents a record to add to the database table
        :return:
        """
        for r in record:
            self.database_manager.queue.put(
                (self._insert_query, r)
            )

    def save_to_csv(self, file_path: Union[str, pathlib.Path] = None) -> pathlib.Path:
        """
        Save the contents of the table from the .db file to a .csv file

        :param file_path: path to save the csv to. default the same path as the .db file with the table name
            appended to the end of it and with a different file path. If the file path already exists, it will be
            overwritten
        :return: the path to the csv file
        """
        if file_path is None:
            file_path = self._csv_path
        table_contents = self.retrieve()

        # create the csv file
        with open(str(file_path.absolute()), mode='wt', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            # write the heading row in the file
            column_names = self.get_table_column_names()
            csv_writer.writerow(column_names)
            for row in table_contents:
                csv_writer.writerow(row)

        return file_path


class TimeBasedDatabaseTable(DatabaseTable):
    def __init__(self, file_path: Union[str, pathlib.Path]):
        """
        A DatabaseTable, with additional methods to retrieve and delete entries based on time; a TimeBasedDatabaseTable
        MUST have a column called 'datetime'

        This is a SQLite3 database table mixin. To use, subclass this class and define the table_name and
        column_name_types. Basic sql injection attack prevention is provided by disallowing the user to set the
        table name and column definitions (defined when the class is defined). There is no protection against imporper
        definition of the subclasses. All subclasses MUST have a column called 'datetime'

        :param file_path: path to the database (.db file)
        """
        column_names = [name for name, value_type in self.column_name_types]
        if 'datetime' not in column_names:
            raise MissingColumnError('datetime must be a column in the table')
        DatabaseTable.__init__(self, file_path)

    def retrieve(self,
                 start_time: datetime = None,
                 end_time: datetime = None,
                 duration: Union[None, timedelta] = timedelta(hours=1),
                 ) -> List[List]:
        """
        Retrieve entries that fall within a time range (inclusive of the start and end times). Must be overwritten
        by the subclass, and the subclass must have a column called "datetime".

        Either provide:
            - start_time and end_time, then duration won't be used
            - start_time and duration, then end_time is start_time + duration
            - end_time and duration, then start_time is end_time - duration
            - only duration, then a default end_time of now is used. if duration is None, then duration is set to 99
            years

        :param start_time: datetime object to denote the start of the time range to retrieve entries
        :param end_time: datetime object to denote the end of the time range to retrieve entries
        :param duration: timedelta object for how long the the time range to retrieves entries is. Default 1 hour
        :return: a list of lists. the inner lists each represent a row from the database, and each value in the inner
            list represents the value for a column index
        """
        if duration is None:
            duration = timedelta(days=365*99)
        if start_time is None and end_time is None:
            end_time = datetime.now()

        if start_time and end_time:
            pass
        elif start_time:
            end_time = start_time + duration
        elif end_time:
            start_time = end_time - duration
        command = self._select_query + " WHERE datetime BETWEEN :start_time AND :end_time"
        values = {
            'start_time': start_time,
            'end_time': end_time,
        }
        with sqlite3.connect(str(self.file_path.absolute())) as db:
            with closing(db.cursor()) as cur:
                cur.execute(command, values)
                rows = cur.fetchall()
        out = []
        for row in rows:
            # cast the datetime column value to the a datetime they should be
            try:
                dt = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                dt = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            # need to typecast values in the concrete class?
            # add the row of values to the output
            r = [dt, *row[1:]]
            out.append(r)
        return out

    def retain(self,
               start_time: datetime = None,
               end_time: datetime = None,
               duration: Union[timedelta, None] = timedelta(days=31),
               ) -> None:
        """
        Only retain the entries that fall within a time range and delete everything else from the database table
        (retain entries that fall on the start and end times).

        'datetime' must be a column in the database table

        Either provide:
            - start_time and end_time, then duration won't be used
            - start_time and duration, then end_time is start_time + duration
            - end_time and duration, then start_time is end_time - duration
            - only duration, then a default end_time of now is used. if None, then the the duration will be 99 years

        https://sqlite.org/lang_delete.html

        :param start_time: datetime object to denote the start of the time range to retain entries
        :param end_time: datetime object to denote the end of the time range to retain entries
        :param duration: timedelta object for how long the the time range to retain entries is. Default 31 days
        :return:
        """
        if 'datetime' not in self.column_names:
            raise MissingColumnError('datetime must be one of the columns in the database')

        if duration is None:
            duration = timedelta(days=365*99)
        if start_time is None and end_time is None:
            end_time = datetime.now()

        if start_time and end_time:
            pass
        elif start_time:
            end_time = start_time + duration
        elif end_time:
            start_time = end_time - duration

        command = self._delete_query + " WHERE datetime NOT BETWEEN :start_time AND :end_time"
        values = {
            'start_time': start_time,
            'end_time': end_time,
        }

        with sqlite3.connect(str(self.file_path.absolute())) as db:
            with closing(db.cursor()) as cur:
                cur.execute(command, values)

    def save_to_csv(self,
                    file_path: Union[str, pathlib.Path] = None,
                    start_time: datetime = None,
                    end_time: datetime = None,
                    duration: Union[timedelta, None] = None,
                    ) -> pathlib.Path:
        """
        Save the contents of the table from the .db file to a .csv file for a given time range

        Either provide:
            - start_time and end_time, then duration won't be used
            - start_time and duration, then end_time is start_time + duration
            - end_time and duration, then start_time is end_time - duration
            - only duration, then a default end_time of now is used,  if None, then the the duration will be 99 years

        :param file_path: path to save the csv to. default the same path as the .db file with the table name
            appended to the end of it and with a different file path. If the file path already exists, it will be
            overwritten
        :param start_time: datetime object to denote the start of the time range to retain entries
        :param end_time: datetime object to denote the end of the time range to retain entries
        :param duration: timedelta object for how long the the time range to retain entries is. Default 99 years
        :return: the path to the csv file
        """
        if file_path is None:
            file_path = self._csv_path
        table_contents = self.retrieve(start_time=start_time,
                                       end_time=end_time,
                                       duration=duration)

        # create the csv file
        with open(str(file_path.absolute()), mode='wt', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            # write the heading row in the file
            column_names = self.get_table_column_names()
            csv_writer.writerow(column_names)
            for row in table_contents:
                csv_writer.writerow(row)

        return file_path


class DatabaseRetentionPolicy(ABC):
    def __init__(self, enabled: bool = False):
        """
        A retention policy that can be run by on a DatabaseTable; it should remove entries from the .db SQLite database
        based on the _retention_policy

        This is an abstract base class. To use, subclass this class and define the _retention_policy. There is no
        protection against improper definition of the subclasses. Since an exact _retention_policy must be defined,
        it is up to the implementor to ensure that the retention policy will successfully execute on the provided
        DatabaseTable instance

        :param enabled: whether to actually execute the retention policy on a DatabaseTable when a
            DatabaseRetentionPolicy instance is called
        """
        self._enabled = enabled

    @property
    @abstractmethod
    def _retention_policy(self) -> str:
        """The exact SQL statement to execute to edit a SQLite .db database table"""
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> bool:
        """Execute the retention policy for the database if the policy is enabled and return whether the retention
        policy was actually run or not"""
        return self._run(*args, **kwargs)

    @property
    @abstractmethod
    def _retention_policy_values(self) -> Dict:
        """Dictionary for the _retention_policy. Keys should match the variables that should be replaced in the
        _retention_policy"""
        raise NotImplementedError

    @property
    def enabled(self) -> bool:
        """Whether the retention policy is enabled and should actually be executed when the DatabaseRetentionPolicy
        instance is called"""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        if value is not None:
            self._enabled = value

    def _run(self, database_table: DatabaseTable) -> bool:
        """
        Execute the retention policy for the database if the policy is enabled

        :param database_table: the DatabaseTable that will run the policy
        :return: bool, whether the retention policy was run or not
        """
        if self.enabled:
            with sqlite3.connect(str(database_table.file_path.absolute())) as db:
                with closing(db.cursor()) as cur:
                    cur.execute(self._retention_policy, self._retention_policy_values)
            return True
        else:
            return False
