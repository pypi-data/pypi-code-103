import pandas as pd


def get_numeric_categorical_columns(df):
    categorical_columns = []
    numeric_columns = []
    for col in df.columns:
        if df[col].map(type).eq(str).any():  # check if there are any strings in column
            categorical_columns.append(col)
        else:
            numeric_columns.append(col)

    # create two DataFrames, one for each data type
    return pd.DataFrame(df[numeric_columns]), pd.DataFrame(df[categorical_columns])
