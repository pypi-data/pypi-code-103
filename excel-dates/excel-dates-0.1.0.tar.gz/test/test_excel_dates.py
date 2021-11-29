import unittest
import datetime

import excel_dates.convert as excel_dates


class TestTemp(unittest.TestCase):
    def test_1(self):
        a = excel_dates.ensure_python_date(10)
        self.assertEqual(datetime.date(1900, 1, 10), a)


if __name__ == "__main__":
    unittest.main(
        failfast=True,
    )
