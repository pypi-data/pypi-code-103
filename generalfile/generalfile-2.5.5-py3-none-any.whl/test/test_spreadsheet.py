
from generalfile import Path
from generalfile.test.test_path import PathTest

import pandas as pd


class FileTest(PathTest):
    @classmethod
    def setUpClass(cls):
        """ . """
        import pandas
        cls.pd = pandas

    def test_tsvWriteAndRead(self):
        self._doTestsOnDataFrame({"a": {"color": "red", "value": 5}, "b": {"color": "blue", "value": 2}})
        self._doTestsOnDataFrame([{"color": "red", "value": 5}, {"color": "blue", "value": 2}])
        self._doTestsOnDataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        self._doTestsOnDataFrame([[1, 2, 3], [4, 5, 6]])

    def test_tsvAppend(self):
        df = pd.DataFrame([[1, 2, 3], [4, 5, 6]])
        self._compareFrames(df, self._appendAndReadDF([[1, 2, 3], [4, 5, 6]]))
        self._compareFrames(df, self._appendAndReadDF([{"a": 1, "b": 2, "c": 3}, {"d": 4, "e": 5, "f": 6}]))
        self._compareFrames(df, self._appendAndReadDF({1: {"b": 2, "c": 3}, 4: {"e": 5, "f": 6}}))
        self._compareFrames(df, self._appendAndReadDF({1: [2, 3], 4: [5, 6]}))

    def _compareFrames(self, df1, df2):
        self.assertEqual(df1.shape, df2.shape)
        self.assertTrue(df1.columns.equals(df2.columns))
        self.assertTrue(df1.index.equals(df2.index))

    def _writeAndReadDF(self, df):
        header, column = Path("df.tsv").spreadsheet.write(df, overwrite=True)
        read = Path("df.tsv").spreadsheet.read(header=header, column=column)
        return read

    def _appendAndReadDF(self, obj):
        Path("df.tsv").spreadsheet.write(pd.DataFrame(), overwrite=True)
        Path("df.tsv").spreadsheet.append(obj)
        read = Path("df.tsv").spreadsheet.read(header=False, column=False)
        return read

    def _doTestsOnDataFrame(self, obj):
        df = pd.DataFrame(obj)
        self._compareFrames(df, self._writeAndReadDF(df))
        self._compareFrames(df.T, self._writeAndReadDF(df.T))

    def test_read_empty(self):
        with self.assertRaises(FileNotFoundError):
            Path("hey").spreadsheet.read()
        self.assertEqual(None, Path("hi").spreadsheet.read(default=None))
