import numpy as np
import pandas as pd

from dataclasses import dataclass

@dataclass
class Data:
    odf: None # Output DataFrame
    idf: None # Input DataFrame

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def display(self, title='Output DataFrame', df='odf'):
        print(f'==== {title} ====\n\n{self[df]}\n')


# Pandas DataFrames

## Displaying
def head(data: Data):
    print(f'==== Output DataFrame ====\n\n{data.odf.head()}\n')
    print(f'==== Input DataFrame ====\n\n{data.idf.head()}\n')

def display(df: pd.DataFrame, title='DataFrame'):
    print(f'==== {title} ====\n\n{df}\n')

## Helper Functions
def shape(df: pd.DataFrame):
    shape = df.shape[0]
    return shape

def copy(data: Data, cols: list[str] = None):
    cols = data.idf.columns.tolist() if cols is None else None
    for col in cols:
        data.odf[col] = data.idf[col].copy()
    return data

def merge(data: pd.DataFrame, arr: np.ndarray, col: str):
    data[col] = pd.DataFrame(arr)
    return data

def expand(data: Data, val, col: str):
    array = np.full(data.idf.shape[0], val)
    return(merge(data, array, col))

def export(df: pd.DataFrame, dest: str, cols: list = None):
    output: pd.DataFrame
    output = df if cols is None else df[cols]
    display(output)
    output.to_csv(dest, index=False)

# Numpy Arrays
def avg(data: Data, col='avg'):
    masses = data.idf[col].to_numpy()
    return np.average(masses)

def stdev(data: Data, col: str):
    return(np.std(data.idf[col].to_numpy()))
