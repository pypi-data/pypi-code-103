from qdk import DataFrameLoader, DataFrameType
from ..utils.dataframe import (
    CSVStoreDataFrame,
    JSONStoreDataFrame,
    PickleStoreDataFrame,
)
from dagster import SolidDefinition, DagsterType


def test_csv_loading(tmpdir):
    """Test loading a csv file.

    Args:
        tmpdir (str): The path to the temporary directory created by pytest
    """
    df_storer = CSVStoreDataFrame()
    df_path = df_storer.store_dataframe(tmpdir)

    loaded_df = DataFrameLoader.load(df_path)
    loaded_ddf = DataFrameLoader.load(df_path, use_dask=True).compute()

    assert loaded_df.equals(df_storer.df)
    assert loaded_ddf.equals(df_storer.df)


def test_json_loading(tmpdir):
    """Test loading a json file.

    Args:
        tmpdir (str): The path to the temporary directory created by pytest
    """
    df_storer = JSONStoreDataFrame()
    df_path = df_storer.store_dataframe(tmpdir)

    loaded_df = DataFrameLoader.load(df_path)
    loaded_ddf = DataFrameLoader.load(df_path, use_dask=True).compute()

    assert loaded_df.equals(df_storer.df)
    assert loaded_ddf.equals(df_storer.df)


def test_pickle_loading(tmpdir):
    """Test loading a pickle file.

    Args:
        tmpdir (str): The path to the temporary directory created by pytest
    """
    df_storer = PickleStoreDataFrame()
    df_path = df_storer.store_dataframe(tmpdir)

    loaded_df = DataFrameLoader.load(df_path)
    loaded_ddf = DataFrameLoader.load(df_path, use_dask=True, repartitions=1).compute()

    assert loaded_df.equals(df_storer.df)
    assert loaded_ddf.equals(df_storer.df)


def test_solid_creation():
    df_loader = DataFrameLoader
    solid = df_loader.to_solid("df_loader")

    assert type(solid) == SolidDefinition


def test_dagster_output_def():
    df_loader = DataFrameLoader
    solid = df_loader.to_solid("df_loader")

    assert len(solid.output_defs) == 1
    assert solid.output_defs[0].dagster_type == DataFrameType
