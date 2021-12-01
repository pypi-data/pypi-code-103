from dagster import (
    DagsterType,
    ModeDefinition,
    PipelineExecutionResult,
    SolidDefinition,
    execute_pipeline,
    pipeline,
)
from dagster.core.execution.results import SolidExecutionResult
from dask.dataframe import DataFrame as DaskDataFrame
from pandas import DataFrame
from qdk import DataFrameLoader, YakeComponent, io_manager

from ..utils.dataframe import CSVStoreDataFrame

loader_solid = DataFrameLoader.to_solid(name="loader")

keyword_solid = YakeComponent.to_solid(
    name="keyword",
)


@pipeline(mode_defs=[ModeDefinition(resource_defs={"io_manager": io_manager})])
def nlp_pipeline():
    df = loader_solid()
    keyword = keyword_solid(df)


def run_pipeline(tmpdir: str, use_dask: bool) -> SolidExecutionResult:
    # Create a temporary dataframe and store it in the temp directory
    df_storer = CSVStoreDataFrame()
    df_path = df_storer.store_dataframe(tmpdir)

    # Execute the pipeline
    result = execute_pipeline(
        nlp_pipeline,
        run_config={
            "solids": {
                "loader": {
                    "config": {
                        "uri": df_path,
                        "use_dask": use_dask,
                    }
                },
                "keyword": {
                    "config": {"language": "en", "text_columns": ["description"]}
                },
            }
        },
    )

    return result


def test_nlp_pipeline(tmpdir):
    # Execute the pipeline
    result = run_pipeline(
        tmpdir,
        use_dask=False,
    )

    result_df = result.output_for_solid("keyword", "df")

    assert result.success
    assert isinstance(result, PipelineExecutionResult)
    assert isinstance(result_df, DataFrame)


def test_nlp_dask_pipeline(tmpdir):
    # Execute the pipeline
    result = run_pipeline(
        tmpdir,
        use_dask=True,
    )

    result_df = result.output_for_solid("keyword", "df")

    assert result.success
    assert isinstance(result, PipelineExecutionResult)
    assert isinstance(result_df, DaskDataFrame)
