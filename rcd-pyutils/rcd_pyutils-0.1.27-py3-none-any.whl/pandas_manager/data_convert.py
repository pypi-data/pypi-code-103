import pandas as pd
from typing import List, Any


def normalize_date_column(df: pd.DataFrame, lst_date_col: List, parse_format: str = None, display_format="%Y-%m-%d",
                          **args: Any) -> pd.DataFrame:
    """
        Function normalize_date_column.
        Parse all date text column into certain format.

        Parameters:
              df (pd.DataFrame): The pandas dataframe that you want to convert to json files.
              lst_date_col (List): The list of date text column names.
              parse_format (str, default None): The fixed date format to parse, auto parse by default.
              display_format (str): The fixed date format to display.

        Examples:
            >>> from rcd_pyutils import file_manager
            >>> file_manager.write_df_to_json_parallel(df=my_dataframe, json_path="my_path")
    """
    df_copy = df.copy()
    for col in lst_date_col:
        try:
            df_copy[col] = pd.to_datetime(df_copy[col].str.strip("-"), format=parse_format, **args) \
                .dt.strftime(display_format)
        except KeyError:
            continue
    return df_copy


def normalize_decimal(df, lst_col, decimal="."):
    df_copy = df.copy()
    for col in lst_col:
        if decimal == ",":
            df_copy[col] = df_copy[col].str.replace(".", "", regex=True)
            df_copy[col] = df_copy[col].str.replace(",", ".", regex=True)
            print(f"✅ Converted decimal from , to . in column {col}")
        elif decimal == ".":
            print(f"✅ Decimal is set to . in column {col}")
        else:
            raise ValueError(f"❓Unrecognized decimal: {decimal} in column {col}")
    return df_copy


def normalize_price_column(df, lst_price_col, decimal=".", **args):
    df_copy = df.copy()
    for col in lst_price_col:
        # Try to convert
        try:
            # Remove text symbols
            df_copy[col] = df_copy[col].str.strip(" —-�€£")
            # Normalize decimal
            if decimal == ",":
                df_copy[col] = df_copy[col].str.replace(".", "", regex=True)
                df_copy[col] = df_copy[col].str.replace(",", ".", regex=True)
            df_copy[col] = pd.to_numeric(df_copy[col].str.strip("-€ "), **args)
        except KeyError:
            continue
    return df_copy


def normalize_percentage_column(df, lst_percentage_col, parse_format="%", decimal="."):
    df_copy = df.copy()
    for col in lst_percentage_col:
        # Try to convert
        try:
            if parse_format == "%":
                df_copy[col] = df_copy[col].str.strip(" %-—")
            # Normalize decimal
            if decimal == ",":
                df_copy[col] = df_copy[col].str.replace(".", "", regex=True)
                df_copy[col] = df_copy[col].str.replace(",", ".", regex=True)
            df_copy[col] = pd.to_numeric(df_copy[col]) / 100
        except KeyError:
            continue
    return df_copy
