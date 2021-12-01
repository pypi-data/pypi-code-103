import pandas as pd
from typing import List


def check_na(df: pd.DataFrame, raise_error: bool = False) -> None:
    """
        Function check_na.
        Use this function to check %na in a pandas dataframe, optional: raise Error if any.

        Args:
            df(pd.DataFrame): The pandas dataframe to check NA.
            raise_error(bool): True to raise Error when there is any NA, by default: True.
        Returns:
            None
        Examples:
            >>> from rcd_pyutils import pandas_manager
            >>> pandas_manager.check_na(df=my_dataframe, raise_error=False)
    """
    print("Checking na by column...")
    df_na_count = df.isna().sum().reset_index().rename(columns={"index": "variable", 0: "na_count"})
    df_na_count["n_row"] = df.shape[0]
    df_na_count["na%"] = round(100 * df_na_count["na_count"] / df_na_count["n_row"], 2).astype(str).apply(
        lambda x: f"{x}%")
    print(df_na_count)
    if raise_error:
        assert len(df_na_count["na_count"].unique().tolist()) == 1, f"There is NA in dataframe."
        print("️⭕️No NA detected!")


def check_duplication(df: pd.DataFrame, lst_col: List, raise_error: bool = False) -> pd.DataFrame:
    """
        Function check_duplication.
        Use this function to check %duplicates in a pandas dataframe, optional: raise Error if any.

        Args:
            df(pd.DataFrame): The pandas dataframe to check duplicates.
            lst_col(list): List of columns name to verify the duplicates.
            raise_error(bool): True to raise Error when there is any duplicates, by default: True.
        Returns:
            None
        Examples:
            >>> from rcd_pyutils import pandas_manager
            >>> pandas_manager.check_duplication(df=my_dataframe, lst_col=["col1", "col2"], raise_error=True)
    """
    print(f"Checking duplication at level {lst_col}...")
    df_copy = df.copy()
    df_dup = df_copy[df_copy.duplicated(subset=lst_col, keep=False)].sort_values(by=lst_col)
    sentence = f"There are {df_dup.shape} duplications which is {round(100 * df_dup.shape[0] / df_copy.shape[0], 2)}% of the whole data."
    if raise_error:
        assert df_dup.shape[0] == 0, sentence
        print("️⭕️No duplication detected!")
    else:
        print(sentence)
    return df_dup
