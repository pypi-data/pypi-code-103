import logging
import pandas as pd  # noqa pandas comes with geopandas


logger = logging.getLogger(__name__)


def df1_rows_not_in_df2(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """
    df1 = pd.DataFrame(data = {'col1' : [1, 2, 3, 4, 5, 3], 'col2' : [10, 11, 12, 13, 14, 10]})
    df2 = pd.DataFrame(data = {'col1' : [1, 2, 3, 4], 'col2' : [10, 11, 12, 16]})
    df_all = df1.merge(df2.drop_duplicates(), how='outer', indicator=True)
    ------------------------
       col1  col2      _merge
    0     1    10        both
    1     2    11        both
    2     3    12        both
    3     4    13   left_only
    4     5    14   left_only
    5     3    10   left_only
    6     4    16  right_only
    ------------------------
    """
    df_all = df1.merge(df2.drop_duplicates(), how="outer", indicator=True)
    return df_all[df_all["_merge"] == "right_only"]


def is_equal_dataframes(
    expected_df: pd.DataFrame, test_df: pd.DataFrame, do_raise: bool = True, check_index: bool = False
) -> bool:
    """A helper function to ensure that a dataframe check result equals an expected dataframe."""
    assert isinstance(expected_df, pd.DataFrame) and isinstance(test_df, pd.DataFrame)
    # ensure ordered dfs (index and column)
    test_df = test_df.sort_index().sort_index(axis=1)
    expected_df = expected_df.sort_index().sort_index(axis=1)

    if not check_index:
        test_df = test_df.reset_index(inplace=False, drop=True)
        expected_df = expected_df.reset_index(inplace=False, drop=True)

    if expected_df.equals(test_df):
        return True
    try:
        assert sorted(test_df.columns) == sorted(expected_df.columns)
        df_too_few_rows = df1_rows_not_in_df2(df1=expected_df, df2=test_df)
        df_too_many_rows = df1_rows_not_in_df2(df1=test_df, df2=expected_df)
        assert df_too_few_rows.empty, f"{len(df_too_few_rows)} too few rows"
        assert df_too_many_rows.empty, f"{len(df_too_many_rows)} too many rows"
    except AssertionError as err:
        logger.error(err)
        if do_raise:
            raise

    try:
        pd.testing.assert_frame_equal(left=test_df, right=expected_df)
        return True
    except Exception as err:
        logger.error(err)
        return False
