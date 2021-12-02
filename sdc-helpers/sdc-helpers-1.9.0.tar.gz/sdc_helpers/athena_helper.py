"""
   SDC Athena helper module
"""
import time
import boto3
import json
from botocore.client import BaseClient

from sdc_helpers import utils
from sdc_helpers.redis_helper import RedisHelper

redis_helper = RedisHelper()

def get_data(
    *,
    query_execution_id: str,
    token: str = None,
    client: BaseClient = None,
):
    if client is None:
        client = boto3.client('athena')

    data = []
    cache_key = f"athena-qeid-{query_execution_id}"
    if token is not None:
        response = client.get_query_results(
            QueryExecutionId=query_execution_id,
            NextToken=token
        )
    else:
        response = client.get_query_results(
            QueryExecutionId=query_execution_id
        )

    rows = utils.dict_query(dictionary=response, path='ResultSet.Rows')

    # Columns are only supplied on the first page

    if token is None:
        columns = [column.get('VarCharValue') for column in rows[0].get('Data')]
        redis_helper.redis_set(
            key=cache_key,
            value=json.dumps(columns),
            expiry=600
        )
    else:
        columns = json.loads(redis_helper.redis_get(key=cache_key))
        if columns is None:
            raise Exception('Could not determine columns. Please investigate')

    count = 0
    for row in rows:
        if count > 0 or token:
            item = {}
            value_index = 0
            for value in row.get('Data'):
                item[columns[value_index]] = value.get('VarCharValue')
                value_index += 1

            data.append(item)

        count += 1

    return data, response.get('NextToken')


def query(
        *,
        query_source: str,
        query_string: str,
        page: bool = False,
        query_bucket: str = 'sdc-athena-queries',
        poll_count: int = 60,
        interval: float = 0.5
):
    """
        Run an Athena query and transform response into list of dictionaries
        Each dictionary is essentially a row of data

        args:
            query_source (str): Source folder in S3 bucket to store response data
            query_string (str): Athena Presto SQL query string
            page (bool): If you don't want all the records at once, page tokens will be returned to retrieve
                         subsequent pages
            query_bucket (str): S3 bucket results will be stored in
                                (Default - sdc-athena-queries)
            poll_count (int): The amount of times the function should check for query completion
                              (Default - 60)
            interval (float): The interval in seconds between polls (Default - 0.5)

        return:
            data (list) : A list of dictionary objects (rows of data)
            token (str): Next page token (only if paging)
    """
    client = boto3.client('athena')
    # pylint: disable=invalid-name,too-many-nested-blocks
    s3_location = "s3://{query_bucket}/{query_source}/".format(
        query_bucket=query_bucket,
        query_source=query_source
    )

    response = client.start_query_execution(
        QueryString=query_string,
        ResultConfiguration={
            'OutputLocation': s3_location,
        },
    )

    query_execution_id = response['QueryExecutionId']

    # we need to now poll the api for when the query has completed
    while poll_count > 0:
        response = client.get_query_execution(
            QueryExecutionId=query_execution_id
        )

        if response['QueryExecution']['Status']['State'] == 'FAILED':
            raise Exception(
                'Athena query failed with error: {error}'.format(
                    error=response['QueryExecution']['Status']
                )
            )

        if response['QueryExecution']['Status']['State'] \
                not in ['QUEUED', 'RUNNING']:
            if page:
                data, token = get_data(client=client, query_execution_id=query_execution_id)
                return query_execution_id, data, token

            all_data = []
            next_token = None
            while True:
                data, next_token = get_data(client=client, query_execution_id=query_execution_id, token=next_token)
                all_data = all_data + data

                if next_token is None:
                    break

            return all_data

        poll_count -= 1
        time.sleep(interval)

    raise Exception('Athena query took too long')
