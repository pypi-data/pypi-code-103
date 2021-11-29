from pdx import Session
from pdx import Console
from pdx import date_service


import unittest
import datetime
import os

out = Console.get()


class TestDates(unittest.TestCase):
    """
    Test the Date functions of pdx-lib
    """

    def test_basics(self):
        """
        Test the Date functions of pdx-lib
        """

        out.put_info("Expecting all dates to be: " + datetime.datetime(2018, 1, 31, 0, 0, 0, 0).strftime('%Y-%m-%d'))

        self.assertTrue(
            date_service.string_to_date("31-JAN-2018") == datetime.datetime(2018, 1, 31, 0, 0, 0, 0),
            "String-to_date #1"
        )
        self.assertTrue(
            date_service.string_to_date("2018-01-31") == datetime.datetime(2018, 1, 31, 0, 0, 0, 0),
            "String-to_date #2"
        )
        self.assertTrue(
            date_service.string_to_date("1/31/2018") == datetime.datetime(2018, 1, 31, 0, 0, 0, 0),
            "String-to_date #3"
        )
        self.assertTrue(
            date_service.string_to_date("1/31/18") == datetime.datetime(2018, 1, 31, 0, 0, 0, 0),
            "String-to_date #4"
        )
        self.assertTrue(
            date_service.string_to_date("01/31/18") == datetime.datetime(2018, 1, 31, 0, 0, 0, 0),
            "String-to_date #5"
        )
        self.assertTrue(
            date_service.string_to_date("01/31/18 1:30:45") == datetime.datetime(2018, 1, 31, 1, 30, 45, 0),
            "String-to_date #6"
        )
        self.assertTrue(
            date_service.string_to_date("01/31/18 1:30") == datetime.datetime(2018, 1, 31, 1, 30, 0),
            "String-to_date #7"
        )
        self.assertTrue(
            date_service.string_to_date("01/31/18 1:30 PM") == datetime.datetime(2018, 1, 31, 13, 30, 0),
            "String-to_date #8"
        )
        self.assertTrue(
            date_service.string_to_date("01/31/18 1:30 pm") == datetime.datetime(2018, 1, 31, 13, 30, 0),
            "String-to_date #9"
        )
        # An error message will be printed here. Suppress it.
        out.suppressConsoleOutput = True
        self.assertTrue(
            date_service.string_to_date("Today at 7:30") is None,
            "String-to_date #10"
        )
        out.suppressConsoleOutput = False


if __name__ == '__main__':
    unittest.main()
