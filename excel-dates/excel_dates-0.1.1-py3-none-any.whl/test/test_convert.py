import datetime
import unittest

from excel_dates import (
    ensure_python_datetime,
    ensure_excel_date,
    ensure_python_date,
    ensure_excel_datetime,
)


class TestEnsurePythonDate(unittest.TestCase):
    def test_1900_leap_year(self):
        self.assertEqual(
            datetime.date(1900, 2, 28),
            ensure_python_date(59),
        )

        with self.assertRaises(ValueError):
            # February 29th, 1900 does not exist in Python.
            ensure_python_date(60)

        self.assertEqual(
            datetime.date(1900, 3, 1),
            ensure_python_date(61),
        )


class TestEnsurePythonDateTime(unittest.TestCase):
    def test_1900_leap_year(self):
        self.assertEqual(
            datetime.datetime(1900, 2, 28, 21, 36),
            ensure_python_datetime(59.9),
        )

        with self.assertRaises(Exception):
            # February 29th, 1900 does not exist in Python.
            ensure_python_datetime(60)

        with self.assertRaises(Exception):
            # February 29th, 1900 does not exist in Python.
            ensure_python_datetime(60.9)

        self.assertEqual(
            datetime.datetime(1900, 3, 1, 0, 0, 0),
            ensure_python_datetime(61),
        )

        self.assertEqual(
            datetime.datetime(1900, 3, 1, 2, 24, 0),
            ensure_python_datetime(61.1),
        )


class TestEnsureExcelDate(unittest.TestCase):
    def test_1900_leap_year(self):
        self.assertEqual(
            59,
            ensure_excel_date(datetime.date(1900, 2, 28)),
        )
        self.assertEqual(
            61,
            ensure_excel_date(datetime.date(1900, 3, 1)),
        )
        self.assertEqual(
            59,
            ensure_excel_date(datetime.datetime(1900, 2, 28, 23, 59, 58)),
        )
        self.assertEqual(
            59,
            ensure_excel_date(datetime.datetime(1900, 2, 28, 23, 59, 59)),
        )
        self.assertEqual(
            61,
            ensure_excel_date(datetime.datetime(1900, 3, 1, 0, 0, 0)),
        )
        self.assertEqual(
            61,
            ensure_excel_date(datetime.datetime(1900, 3, 1, 0, 0, 1)),
        )


class TestEnsureExcelDateTime(unittest.TestCase):
    def test_1900_leap_year(self):
        self.assertEqual(
            59.0,
            ensure_excel_datetime(datetime.date(1900, 2, 28)),
        )
        self.assertEqual(
            61.0,
            ensure_excel_datetime(datetime.date(1900, 3, 1)),
        )
        self.assertEqual(
            59.99998,
            round(ensure_excel_datetime(datetime.datetime(1900, 2, 28, 23, 59, 58)), 5),
        )
        self.assertEqual(
            59.99999,
            round(ensure_excel_datetime(datetime.datetime(1900, 2, 28, 23, 59, 59)), 5),
        )
        self.assertEqual(
            61.0,
            ensure_excel_datetime(datetime.datetime(1900, 3, 1, 0, 0, 0)),
        )
        self.assertEqual(
            61.00001,
            round(ensure_excel_datetime(datetime.datetime(1900, 3, 1, 0, 0, 1)), 5),
        )


if __name__ == "__main__":
    unittest.main(
        failfast=True,
    )
