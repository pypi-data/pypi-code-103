from django.test import TestCase
from djangopyetl.admin import StgTable

# Create your tests here.


class TestStgTable(TestCase):
    def setUp(self):
        table_name = "TestTable"
        cols = ["id", "name", "date", "active"]
        cutoff_date_table = "1900-01-01"
        cutoff_cols = []
        query = ""
        self.stg = StgTable(table_name, cols, cutoff_date_table, cutoff_cols, query)

    def test_str(self):
        expected = (
            "StgTable(TestTable, ['id', 'name', 'date', 'active'], 1900-01-01, [])"
        )

        self.assertEqual(expected, self.stg.__str__())

    def test_construct_query_null_query(self):
        expected = "SELECT id, name, date, active FROM TestTable"

        self.assertEquals(
            expected, self.stg.construct_query(self.stg.cutoff_date_table)
        )

    def test_construct_query_notnull_query(self):
        self.stg.query = "SELECT min(id) FROM TestTable"
        expected = "SELECT * FROM (SELECT min(id) FROM TestTable) a"

        self.assertEquals(expected, self.stg.construct_query())

    def test_construct_query_one_cutoff_col(self):
        self.stg.cutoff_cols = ["date"]
        expected = "SELECT id, name, date, active FROM TestTable WHERE (CAST(date as DATE) >= CAST('1900-01-01' as DATE))"

        self.assertEquals(expected, self.stg.construct_query())

    def test_construct_query_cutoff_date(self):
        self.stg.cutoff_cols = ["date"]
        expected = "SELECT id, name, date, active FROM TestTable WHERE (CAST(date as DATE) >= CAST('2021-01-01' as DATE))"

        self.assertEquals(expected, self.stg.construct_query("2021-01-01"))

    def test_construct_query_cutoff_col_and_cutoff_and_limit_date(self):
        self.stg.cutoff_cols = ["date"]
        expected = "SELECT id, name, date, active FROM TestTable WHERE (CAST(date as DATE) >= CAST('2021-01-01' as DATE)AND CAST(date as DATE) <= CAST('2021-02-01' as DATE))"

        self.assertEquals(
            expected, self.stg.construct_query("2021-01-01", "2021-02-01")
        )

    def test_construct_query_two_cutoff_col(self):
        self.stg.cutoff_cols = ["date", "active"]
        expected = "SELECT id, name, date, active FROM TestTable WHERE (CAST(date as DATE) >= CAST('1900-01-01' as DATE)) OR (CAST(active as DATE) >= CAST('1900-01-01' as DATE))"

        self.assertEquals(expected, self.stg.construct_query())

    def test_construct_query_two_cutoff_col_and_cutoff_date(self):
        self.stg.cutoff_cols = ["date", "active"]
        expected = "SELECT id, name, date, active FROM TestTable WHERE (CAST(date as DATE) >= CAST('2021-01-01' as DATE)) OR (CAST(active as DATE) >= CAST('2021-01-01' as DATE))"

        self.assertEquals(expected, self.stg.construct_query("2021-01-01"))

    def test_construct_query_two_cutoff_col_and_cutoff_and_limit_date(self):
        self.stg.cutoff_cols = ["date", "active"]
        expected = "SELECT id, name, date, active FROM TestTable WHERE (CAST(date as DATE) >= CAST('2021-01-01' as DATE)AND CAST(date as DATE) <= CAST('2021-02-01' as DATE)) OR (CAST(active as DATE) >= CAST('2021-01-01' as DATE)AND CAST(active as DATE) <= CAST('2021-02-01' as DATE))"

        self.assertEquals(
            expected, self.stg.construct_query("2021-01-01", "2021-02-01")
        )
