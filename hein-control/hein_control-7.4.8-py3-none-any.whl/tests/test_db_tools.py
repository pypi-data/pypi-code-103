"""
Tests database tools
"""
import csv
import pathlib
import time
import unittest
from pathlib import Path
import threading
from typing import List, Tuple, Dict

import sqlite3
from contextlib import closing
from datetime import datetime, timedelta

from hein_control.db_tools import DatabaseTable, TimeBasedDatabaseTable, MissingColumnError, DatabaseRetentionPolicy, DatabaseManager

lock = threading.Lock()


def run_locked(func):
    """decorator to run a function using a lock"""
    def wrapper(*args, **kwargs):
        with lock:
            func(*args, **kwargs)
    return wrapper


def _read_csv(file_path) -> str:
    """Read and return the contents of a csv file"""
    with open(file_path, newline='') as file:
        csv_reader = csv.reader(file, delimiter=',')
        csv_contents = ''
        for row in csv_reader:
            csv_contents += ','.join(row)
    return csv_contents


class TestDatabaseTable(TimeBasedDatabaseTable):
    @property
    def table_name(self) -> str:
        return 'TEST_DB_TABLE'

    @property
    def column_name_types(self) -> List[Tuple[str, str]]:
        return [
            ('datetime', 'DATE'),
            ('col_1', 'TEXT'),
            ('col_2', 'REAL'),
            ('col_3', 'BOOL'),
        ]


class BadTestTimeBasedDatabaseTable(TimeBasedDatabaseTable):
    @property
    def column_name_types(self) -> List[Tuple[str, str]]:
        return [
            ('col_1', 'TEXT'),
            ('col_2', 'REAL'),
            ('col_3', 'BOOL'),
        ]

    @property
    def table_name(self) -> str:
        return 'A_BAD_TEMPORAL_TEST_DB_TABLE'

class AnotherTestDatabaseTable(DatabaseTable):
    @property
    def column_name_types(self) -> List[Tuple[str, str]]:
        return [
            ('col_1', 'TEXT'),
            ('col_2', 'REAL'),
            ('col_3', 'BOOL'),
        ]

    @property
    def table_name(self) -> str:
        return 'ANOTHER_TEST_DB_TABLE'


class TestDatabaseTable31DayRetentionPolicy(DatabaseRetentionPolicy):
    """A policy to only retain entries made within the last 31 days, any entries exactly at the end time will not be
    retained"""
    @property
    def _retention_policy(self) -> str:
        policy = "delete from TEST_DB_TABLE where datetime not between :start_time and :end_time"
        return policy

    @property
    def _retention_policy_values(self) -> Dict:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=31)
        values = {
            'start_time': start_time,
            'end_time': end_time,
        }
        return values


class TestDBTools(unittest.TestCase):

    db_path: str = 'test_db.db'
    db_path_without_file_type: str = 'test_db'
    db_time_based_table: TimeBasedDatabaseTable = None
    db_retention_policy_31_days: TestDatabaseTable31DayRetentionPolicy = TestDatabaseTable31DayRetentionPolicy(enabled=False)

    def setUp(self) -> None:
        if Path(self.db_path).exists():
            # delete any existing db files
            Path(self.db_path).unlink()
        self.db_time_based_table = TestDatabaseTable(file_path=self.db_path)

    def tearDown(self) -> None:
        DatabaseManager.stop_all_instances()
        time.sleep(0.5)
        if Path(self.db_path).exists():
            # delete any existing db files
            Path(self.db_path).unlink()

    def test_db_extension(self):
        """tests db basic setting"""
        self.assertIsInstance(self.db_time_based_table.file_path, pathlib.Path, 'ensure table path is pathlib.Path')
        self.assertEqual(self.db_time_based_table.file_path.suffix, '.db', 'ensure extension exists')

    @run_locked
    def test_db_basic_properties(self):
        table_names = self.db_time_based_table.db_table_names
        self.assertIn('TEST_DB_TABLE', table_names, 'the table name should be contained in the db table')

        column_names = self.db_time_based_table.column_names
        self.assertEqual(4, len(column_names), 'there should only be 3 columns in the database')
        for index in range(4):
            if index == 0:
                self.assertEqual('datetime', column_names[index])
            else:
                col_number = index
                self.assertEqual(f'col_{col_number}', column_names[index])

    @run_locked
    def test_database_table_insert_retrieve(self):
        another_db_table = AnotherTestDatabaseTable(file_path=self.db_path)
        expected_entries = []
        for i in range(5):
            expected_entries.append([f'text {i}', i, True if i % 2 == 0 else False])
            another_db_table.insert((f'text {i}', i, True if i % 2 == 0 else False))
            time.sleep(0.5)
            retrieved = another_db_table.retrieve()
            self.assertEqual(expected_entries, retrieved,
                             'ensure all entries were inserted and retrieved properly')

        # test inserting multiple values at once
        expected_entries.append([f'text {5}', 5, True if 5 % 2 == 0 else False])
        expected_entries.append([f'text {6}', 6, True if 6 % 2 == 0 else False])
        another_db_table.insert(*[(f'text {5}', 5, True if 5 % 2 == 0 else False),
                                  (f'text {6}', 6, True if 6 % 2 == 0 else False),
                                  ])
        time.sleep(0.5)
        retrieved = another_db_table.retrieve()
        self.assertEqual(expected_entries, retrieved,
                         'ensure inserting multiple values at once works')

    @run_locked
    def test_time_based_table_insert_retrieve_remove(self):
        wait_time = 1  # second, wait time between inserting data into the table

        # test inserting into the database table
        insert_1_time = datetime.now()
        insert_1 = (insert_1_time, 'insert 1', 1, True)
        self.db_time_based_table.insert(insert_1)
        time.sleep(0.5)
        expected_1 = [list(insert_1)]
        retrieve_1 = self.db_time_based_table.retrieve()
        self.assertEqual(expected_1, retrieve_1, 'ensure only 1 row with the correct values')
        time.sleep(wait_time)

        insert_2_time = datetime.now()
        insert_2 = (insert_2_time, 'insert 2', 2, True)
        self.db_time_based_table.insert(insert_2)
        time.sleep(0.5)
        expected_1_and_2 = [list(insert_1), list(insert_2)]
        retrieve_1_and_2 = self.db_time_based_table.retrieve()
        self.assertEqual(expected_1_and_2, retrieve_1_and_2, 'ensure both rows returned with the correct values')
        time.sleep(wait_time)

        insert_3_time = datetime.now()
        insert_3 = (insert_3_time, 'insert 3', 3, False)
        self.db_time_based_table.insert(insert_3)
        time.sleep(wait_time)

        insert_4_time = datetime.now()
        insert_4 = (insert_4_time, 'insert 4', 4, False)
        self.db_time_based_table.insert(insert_4)
        time.sleep(wait_time)

        insert_5_time = datetime.now()
        insert_5 = (insert_5_time, 'insert 5', 5, False)
        self.db_time_based_table.insert(insert_5)
        time.sleep(0.5)
        expected_1_and_2_and_3_and_4_and_5 = [list(insert_1), list(insert_2), list(insert_3), list(insert_4),
                                              list(insert_5)]
        retrieve_1_and_2_and_3_and_4_and_5 = self.db_time_based_table.retrieve()
        self.assertEqual(expected_1_and_2_and_3_and_4_and_5,
                         retrieve_1_and_2_and_3_and_4_and_5,
                         'ensure all five rows returned with the correct values')

        # test that retrieving data within specific timeframes work
        expected_1_and_2_and_3 = [list(insert_1), list(insert_2), list(insert_3)]
        retrieve_1_and_2_and_3 = self.db_time_based_table.retrieve(start_time=insert_1_time, end_time=insert_3_time)
        self.assertEqual(expected_1_and_2_and_3, retrieve_1_and_2_and_3,
                         'ensure retrieving from a start time & end time works')

        expected_2_and_3_and_4 = [list(insert_2), list(insert_3), list(insert_4)]
        # use duration of wait_time * 2.5 instead of 2 as a bit of a fudge factor for the time it takes to run code
        retrieve_2_and_3_and_4 = self.db_time_based_table.retrieve(start_time=insert_2_time, duration=timedelta(seconds=wait_time * 3))
        self.assertEqual(expected_2_and_3_and_4,
                         retrieve_2_and_3_and_4,
                         'ensure retrieving from a start time & duration works')

        expected_3_and_4 = [list(insert_3), list(insert_4)]
        # use duration of wait_time * 2.5 instead of 2 as a bit of a fudge factor for the time it takes to run code
        retrieve_3_and_4 = self.db_time_based_table.retrieve(end_time=insert_4_time, duration=timedelta(seconds=wait_time * 1.5))
        self.assertEqual(expected_3_and_4, retrieve_3_and_4,
                         'ensure retrieving from an end time & duration works')

        # test retaining rows only within specific times
        self.db_time_based_table.retain(start_time=insert_2_time, end_time=insert_5_time)
        expected_2_and_3_and_4_and_5 = [list(insert_2), list(insert_3), list(insert_4), list(insert_5)]
        retrieve_2_and_3_and_4_and_5 = self.db_time_based_table.retrieve()
        self.assertEqual(expected_2_and_3_and_4_and_5, retrieve_2_and_3_and_4_and_5,
                         'ensure retrieving from a start time & end time works')

        self.db_time_based_table.retain(start_time=insert_2_time, duration=insert_4_time - insert_2_time)
        expected_2_and_3_and_4 = [list(insert_2), list(insert_3), list(insert_4)]
        retrieve_2_and_3_and_4 = self.db_time_based_table.retrieve()
        self.assertEqual(expected_2_and_3_and_4, retrieve_2_and_3_and_4,
                         'ensure retrieving from a start time & duration works')

        self.db_time_based_table.retain(end_time=insert_4_time, duration=insert_4_time - insert_3_time)
        expected_3_and_4 = [list(insert_3), list(insert_4)]
        retrieve_3_and_4 = self.db_time_based_table.retrieve()
        self.assertEqual(expected_3_and_4, retrieve_3_and_4,
                         'ensure retrieving from an end time & duration works')

        # test retrieve and retain with default values works
        insert_31_days_ago_time = datetime.now() - timedelta(days=31, seconds=1)
        insert_31_days_ago = (insert_31_days_ago_time, 'insert 31 days ago', -31, True)
        self.db_time_based_table.insert(insert_31_days_ago)
        time.sleep(0.5)

        retrieve_3_and_4 = self.db_time_based_table.retrieve()
        self.assertEqual(expected_3_and_4, retrieve_3_and_4,
                         'ensure retrieving with defaults end time now duration 1 hour works')

        expected_3_and_4_and_neg31 = [list(insert_3), list(insert_4), list(insert_31_days_ago)]
        retrieve_3_and_4_and_neg31 = self.db_time_based_table.retrieve(duration=timedelta(days=32))
        self.assertEqual(expected_3_and_4_and_neg31, retrieve_3_and_4_and_neg31,
                         'ensure retrieving older than the default duration of 31 days works')

        self.db_time_based_table.retain()
        retrieve_3_and_4 = self.db_time_based_table.retrieve(duration=None)
        self.assertEqual(expected_3_and_4, retrieve_3_and_4,
                         'ensure retaining with default end time now duration 1 hour works')

    @run_locked
    def test_retention_policy(self):
        self.assertFalse(self.db_retention_policy_31_days.enabled, 'retention policy should not be enabled')

        self.db_retention_policy_31_days.enabled = True
        self.assertTrue(self.db_retention_policy_31_days.enabled, 'retention policy should be enabled')

        self.db_retention_policy_31_days.enabled = False
        self.assertFalse(self.db_retention_policy_31_days.enabled, 'retention policy should not be enabled')

        # initially add values into the database table
        insert_1_time = datetime.now()
        insert_1 = (insert_1_time, 'insert 1', 1, True)
        self.db_time_based_table.insert(insert_1)

        insert_almost_31_days_ago_time = datetime.now() - timedelta(days=30, hours=23, minutes=59)
        insert_almost_31_days_ago = (insert_almost_31_days_ago_time, 'insert almost 31 days ago', -31, True)
        self.db_time_based_table.insert(insert_almost_31_days_ago)

        insert_31_days_ago_time = datetime.now() - timedelta(days=31)
        insert_31_days_ago = (insert_31_days_ago_time, 'insert 31 days ago', -31, True)
        self.db_time_based_table.insert(insert_31_days_ago)

        insert_32_days_ago_time = datetime.now() - timedelta(days=32)
        insert_32_days_ago = (insert_32_days_ago_time, 'insert 32 days ago', -32, True)
        self.db_time_based_table.insert(insert_32_days_ago)
        time.sleep(0.5)

        # run the policy on the database table, but dont enable the policy so the values should not be removed
        expected_1_and_almost_31_and_31_and_32 = [list(insert_1), list(insert_almost_31_days_ago), list(insert_31_days_ago), list(insert_32_days_ago)]
        self.assertFalse(self.db_retention_policy_31_days(self.db_time_based_table),
                         'policy should not run because it is not enabled')
        retrieved_1_and_almost_31_and_31_and_32 = self.db_time_based_table.retrieve(duration=None)
        self.assertEqual(expected_1_and_almost_31_and_31_and_32, retrieved_1_and_almost_31_and_31_and_32,
                         'all entries should be in the database if duration is None')

        # run the policy on the database table with the policy enabled so values older than 31 days should be removed
        self.db_retention_policy_31_days.enabled = True
        self.assertTrue(self.db_retention_policy_31_days.enabled, 'retention policy should now be enabled')
        expected_1_and_almost_31 = [list(insert_1), list(insert_almost_31_days_ago)]
        policy_ran = self.db_retention_policy_31_days(self.db_time_based_table)
        self.assertTrue(policy_ran,
                        'policy should run because it is enabled')
        retrieved_1_and_almost_31 = self.db_time_based_table.retrieve(duration=None)
        self.assertEqual(expected_1_and_almost_31, retrieved_1_and_almost_31,
                         'the 32 day old entry should be removed and only the other two entries should remain')

    @run_locked
    def test_adding_second_table(self):
        # test adding a second table to the database
        another_db_table = AnotherTestDatabaseTable(file_path=self.db_path)

        table_names = another_db_table.db_table_names
        self.assertEqual(2, len(table_names), 'there should only be 2 tables in the database')
        self.assertEqual(['TEST_DB_TABLE', 'ANOTHER_TEST_DB_TABLE'], table_names,
                         'the database table names should match')

    @run_locked
    def test_dont_add_a_bad_table(self):
        # should not be able to instantiate this TimeBasedDatabaseTable because datetime is not a column
        with self.assertRaises(MissingColumnError) as cm:
            BadTestTimeBasedDatabaseTable(file_path=self.db_path)
        self.assertEqual(cm.exception.msg, 'datetime must be a column in the table', 'ensure MissingColumnError was thrown')

    def test_basic_protection(self):
        """tests the basic sqlite injection prevention"""
        for attr in ['_base_query', 'table_name']:
            self.assertRaises(
                AttributeError,
                setattr,
                self.db_time_based_table,
                attr,
                'malicious value'
            )

    @run_locked
    def test_save_to_csv(self):
        """test saving tables into a csv file"""
        basic_db_table_csv_heading = 'col_1,col_2,col_3'
        db_time_based_table_csv_heading = 'datetime,col_1,col_2,col_3'

        # add a second table to the database to make sure data from different tables in the same database get saved
        # in separate csv files
        basic_db_table = AnotherTestDatabaseTable(file_path=self.db_path)
        basic_db_table_csv_path = Path('test save csv.csv')

        # ensure the default csv file path is set properly
        self.assertEqual(self.db_time_based_table._csv_path,
                         Path(f'{self.db_path_without_file_type} - {self.db_time_based_table.table_name}.csv').absolute(),
                         'ensure the default csv file path is set properly')

        # if any csv files from previous tests exist, remove them
        if self.db_time_based_table._csv_path.exists():
            self.db_time_based_table._csv_path.unlink()
        if basic_db_table_csv_path.exists():
            basic_db_table_csv_path.unlink()
        self.assertFalse(self.db_time_based_table._csv_path.exists(),
                         'ensure creating a csv with the default csv name works')
        self.assertFalse(basic_db_table_csv_path.exists(),
                         'ensure creating a csv with the default csv name works')

        # ensure the initial csv files have the correct headings and file names
        basic_db_table.save_to_csv(file_path=basic_db_table_csv_path)
        self.db_time_based_table.save_to_csv()
        self.assertTrue(self.db_time_based_table._csv_path.exists(),
                        'ensure creating a csv with the default csv name works')
        self.assertTrue(basic_db_table_csv_path.exists(),
                        'ensure creating a csv with a custom csv name works')
        csv_contents = _read_csv(basic_db_table_csv_path)
        self.assertEqual(csv_contents, basic_db_table_csv_heading,
                         'ensure the heading row for the basic db table was created correctly')
        csv_contents = _read_csv(self.db_time_based_table._csv_path)
        self.assertEqual(csv_contents, db_time_based_table_csv_heading,
                         'ensure the heading row for the time based db table was created correctly')

        entry_times = [datetime(year=2019, month=9, day=30, hour=i, minute=0, second=0, microsecond=0) for i in range(6)]

        #  insert values into the database tables, save the tables as csv files, and ensure the contents are correct
        expected_basic_db_table_csv_contents = basic_db_table_csv_heading
        expected_time_based_db_table_csv_contents = db_time_based_table_csv_heading
        for i, entry_time in enumerate(entry_times):
            i = float(i)
            basic_db_table.insert((f'text {i}', i, True if i % 2 == 0 else False))
            self.db_time_based_table.insert((entry_time, f'text {i}', i, True if i % 2 == 0 else False))
            time.sleep(0.5)
            # save the csv files
            basic_db_table.save_to_csv(basic_db_table_csv_path)
            self.db_time_based_table.save_to_csv()
            # ensure the csv updates properly
            expected_basic_db_table_csv_contents += f'text {i},{i},{1 if i % 2 == 0 else 0}'
            expected_time_based_db_table_csv_contents += f'{datetime.strftime(entry_time, "%Y-%m-%d %H:%M:%S")},text {i},{i},{1 if i % 2 == 0 else 0}'
            csv_contents = _read_csv(basic_db_table_csv_path)
            self.assertEqual(csv_contents, expected_basic_db_table_csv_contents,
                             'ensure the contents of the basic db table were saved to the csv correctly')
            csv_contents = _read_csv(self.db_time_based_table._csv_path)
            self.assertEqual(csv_contents, expected_time_based_db_table_csv_contents,
                             'ensure the contents of the time based db table were saved to the csv correctly')

        # test saving only certain times for the time based database table
        self.db_time_based_table.save_to_csv(start_time=datetime(year=2019, month=9, day=30, hour=2, minute=0, second=0, microsecond=0),
                                             end_time=datetime(year=2019, month=9, day=30, hour=4, minute=0, second=0, microsecond=0),
                                             )
        csv_contents = _read_csv(self.db_time_based_table._csv_path)
        expected = "datetime,col_1,col_2,col_3" \
                   "2019-09-30 02:00:00,text 2.0,2.0,1" \
                   "2019-09-30 03:00:00,text 3.0,3.0,0" \
                   "2019-09-30 04:00:00,text 4.0,4.0,1"
        self.assertEqual(csv_contents, expected,
                         'ensure saving a csv with a start time and end time works')

        self.db_time_based_table.save_to_csv(start_time=datetime(year=2019, month=9, day=30, hour=0, minute=0, second=0, microsecond=0),
                                             duration=timedelta(hours=3),
                                             )
        csv_contents = _read_csv(self.db_time_based_table._csv_path)
        expected = "datetime,col_1,col_2,col_3" \
                   "2019-09-30 00:00:00,text 0.0,0.0,1" \
                   "2019-09-30 01:00:00,text 1.0,1.0,0" \
                   "2019-09-30 02:00:00,text 2.0,2.0,1" \
                   "2019-09-30 03:00:00,text 3.0,3.0,0"
        self.assertEqual(csv_contents, expected,
                         'ensure saving a csv with a start and duration works')

        self.db_time_based_table.save_to_csv(end_time=datetime(year=2019, month=9, day=30, hour=4, minute=0, second=0, microsecond=0),
                                             duration=timedelta(hours=2),
                                             )
        csv_contents = _read_csv(self.db_time_based_table._csv_path)
        expected = "datetime,col_1,col_2,col_3" \
                   "2019-09-30 02:00:00,text 2.0,2.0,1" \
                   "2019-09-30 03:00:00,text 3.0,3.0,0" \
                   "2019-09-30 04:00:00,text 4.0,4.0,1"
        self.assertEqual(csv_contents, expected,
                         'ensure saving a csv with an end time and duration works')





