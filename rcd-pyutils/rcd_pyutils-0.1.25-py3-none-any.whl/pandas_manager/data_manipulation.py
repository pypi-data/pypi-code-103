import pandas as pd


def strip_all_text_column(df: pd.DataFrame) -> pd.DataFrame:
    """
        Function strip_all_text_column.
        Use this function to strip all the text columns.

        Args:
            df(pd.DataFrame): The pandas dataframe to strip.
        Returns:
            pd.DataFrame: The stripped pandas dataframe.
        Examples:
            >>> from rcd_pyutils import pandas_manager
            >>> pandas_manager.strip_all_text_column(df=my_dataframe)
    """
    df_obj = df.select_dtypes(["object"])
    df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())
    return df