import os.path
import platform
import numpy as np
import pandas as pd
from ..utils.base_func import trans2D, trans1D

class DataObject(object):

    def __init__(self, X=None, Y=None, Xnames=None, indexes=None, Yname=None):
        self.X = X
        self.Y = Y
        self.Xnames = Xnames
        self.indexes = indexes
        self.Yname = Yname
        if X is not None:
            self.check()
    
    def check(self):
        self.X = trans2D(self.X)
        self.Y = trans1D(self.Y)
        try:
            self.X = self.X.astype(float)
            self.Y = self.Y.astype(float)
        except:
            pass
        if self.Xnames is None:
            self.Xnames = np.arange(self.X.shape[1])
        if self.Yname is None:
            self.Yname = "target"
        if self.indexes is None:
            self.indexes = np.arange(self.X.shape[0])
        self.Xnames = trans1D(self.Xnames)
        self.indexes = trans1D(self.indexes)
        self.Yname = trans1D(self.Yname)
        return self

    def from_df(self, df, tari=0):
        values = df.values
        columns = df.columns.values
        self.Y = values[:, tari]
        self.X = np.delete(values, tari, axis=1)
        self.Xnames = np.delete(columns, tari)
        self.Yname = columns[tari]
        self.indexes = df.index
        return self
    
    def to_df(self):
        self.check()
        return pd.DataFrame(np.concatenate([trans2D(self.Y), self.X], axis=1), index=self.indexes, columns=self.Yname.tolist()+self.Xnames.tolist())

    def copy(self):
        import copy
        return copy.deepcopy(self)

class ReadFromFile(object):

    def __init__(self, filepath, number_index=0, target_index=1, **kwargs):
        self.filepath = filepath
        self.numi = number_index
        self.tari = target_index
        self.read_data()

    @property
    def ext(self):
        return os.path.splitext(self.filepath)[-1]

    @property
    def line_spliter(self):
        if platform.system() == "Windows":
            return "\r\n"
        else:
            return "\n"

    @property
    def spliter(self):
        if self.ext == ".txt":
            return "\t"
        elif self.ext == ".csv":
            return ","

    def read_from_excel(self):
        self.df = pd.read_excel(self.filepath, index_col=self.numi)

    def read_from_csv_or_txt(self):
        with open(self.filepath, "r", newline=self.line_spliter) as f:
            if f.readable():
                row_list = []
                for index, line in enumerate(f.readlines()):
                    row = [cell for cell in line.split(self.line_spliter)[0].split(self.spliter)]
                    if index == 0:
                        columns = row
                    else:
                        row_list.append(row)
                row_array = np.array(row_list)
                # row_array = np.concatenate([row_array[:, self.numi], np.delete(row_array, self.numi, axis=1)])
                self.df = pd.DataFrame(np.delete(row_array, self.numi, axis=1), index=row_array[:, self.numi], columns=columns[1:])
            else:
                raise Exception(f"Unreadable file: {self.filepath}")

    def read_data(self):
        if self.ext in [".xlsx", ".xls"]:
            self.read_from_excel()
        elif self.ext in [".txt", ".csv"]:
            self.read_from_csv_or_txt()

    @property
    def dataobject(self):
        return DataObject().from_df(self.df, self.tari-1)


def read_data(filepath, df=True, *args):
    if df:
        return ReadFromFile(filepath, *args).df
    else:
        return ReadFromFile(filepath, *args).dataobject

