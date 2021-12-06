from typing import List, Dict, Any
import time


def _wait_for_query_completion(athena_client, query_id):
    _QUERY_FINAL_STATES: List[str] = ["FAILED", "SUCCEEDED", "CANCELLED"]
    response = athena_client.get_query_execution(QueryExecutionId=query_id)
    state = response["QueryExecution"]["Status"]["State"]
    while state not in _QUERY_FINAL_STATES:
        time.sleep(1)
        response = athena_client.get_query_execution(QueryExecutionId=query_id)
        state = response["QueryExecution"]["Status"]["State"]
    if state == "FAILED":
        print(response["QueryExecution"]["Status"]["StateChangeReason"])
    if state == "CANCELLED":
        print(response["QueryExecution"]["Status"]["StateChangeReason"])
    if state == "SUCCEEDED":
        return state


def _update_column_coments(
    column_comments: Dict[str, str], glue_client, database: str, table_name: str,
):
    try:
        response = glue_client.get_table(DatabaseName=database, Name=table_name,)
        table_input: Dict[str, Any] = {}
        for k, v in response["Table"].items():
            if k in [
                "Name",
                "Description",
                "Owner",
                "LastAccessTime",
                "LastAnalyzedTime",
                "Retention",
                "StorageDescriptor",
                "PartitionKeys",
                "ViewOriginalText",
                "ViewExpandedText",
                "TableType",
                "Parameters",
                "TargetTable",
            ]:
                table_input[k] = v

        for col in table_input["StorageDescriptor"]["Columns"]:
            if col["Name"] in column_comments.keys():
                col["Comment"] = column_comments[col["Name"]]

        glue_client.update_table(
            DatabaseName=database, TableInput=table_input,
        )
    except Exception as e:
        raise e


def _generate_create_statement(
    query: str,
    database: str,
    table_name: str,
    bucket: str,
    bucket_prefix: str,
    bucketed_columns: List[str] = None,
    bucketed_count: int = None,
    partition_column: List[str] = None,
):

    create_statement = f"""
    CREATE TABLE {database}.{table_name}
    WITH (

        format='PARQUET',
        write_compression = 'SNAPPY',
        external_location = 's3://{bucket}/{bucket_prefix}'"""

    if partition_column is not None:
        if type(partition_column) != list:
            partition_column = [partition_column]

        partition_statement = f"""
        partitioned_by = ARRAY{partition_column}"""
        create_statement = f"""{create_statement}, {partition_statement}"""

    if bucketed_columns is not None:
        if type(bucketed_columns) != list:
            bucketed_column = [bucketed_columns]

        bucketed_statement = f"""
        bucketed_by = ARRAY{bucketed_column},
        bucket_count = {bucketed_count}"""
        create_statement = f"""{create_statement}, {bucketed_statement}"""

    query = f"""{create_statement}) AS {query}"""
    return query


if __name__ == "__main__":
    query = """
            SELECT
              A. ID
            , uuid() NEW_ID
            , A. KEY_
            , A. DATA_IND
            , A. HOUR_MIN
            , A. ORIG
            , A. DES
            , A. EQP
        
    """

    query = _generate_create_statement(
        query,
        database="test_db",
        table_name="table_name",
        bucket="mlops",
        bucket_prefix="bucket_prefix",
        bucketed_column=["KEY_", "ORIG"],
        bucketed_count=3,
        partition_column=["EQP"],
    )
    print(query)
