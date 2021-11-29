import logging
import os
from typing import Optional, Union, Tuple

from humanfriendly import format_size

from dslib.utils import timeit

try:
    import pandas as pd
    from google.cloud import bigquery
    from google.api_core.exceptions import BadRequest, GoogleAPIError
    from google.cloud.bigquery_storage import BigQueryReadClient
except ImportError as e:
    raise ImportError('Please install "google" extra packages.') from e

# Set up logger
LOGGER = logging.getLogger(__name__)
logging.getLogger('google.auth._default').setLevel(logging.ERROR)  # Silence google auth warning/info/debug logs
logging.getLogger('pandas_gbq.gbq').setLevel(logging.WARNING)  # Silence pandas GBQ info/debug logs

# Set up special types
JobType = bigquery.job._AsyncJob


class BigQueryError(Exception):
    pass


class BigQueryWrapper(object):

    def __init__(self, client: bigquery.Client, bqstorage_client: BigQueryReadClient = None) -> None:
        if not client.__class__.__name__ == 'Client':
            raise ValueError('"client" argument must be a Google "Client" instance')
        self.client = client
        self._bqstorage_client = bqstorage_client

    @classmethod
    def from_params(cls, project: str, auth_file: Optional[str] = None, setup_bqstorage: bool = True):
        if auth_file:
            if not os.path.exists(auth_file):
                raise FileNotFoundError(f'Authentication file does not exist: {auth_file}')
            client = bigquery.Client.from_service_account_json(auth_file, **{'project': project})
            bqstorage_client = BigQueryReadClient.from_service_account_json(auth_file) if setup_bqstorage else None
        else:
            client = bigquery.Client(project=project)
            bqstorage_client = BigQueryReadClient() if setup_bqstorage else None
        return BigQueryWrapper(client, bqstorage_client)

    @property
    def bqstorage_client(self):
        if self._bqstorage_client is None:
            raise BigQueryError('BigQuery Storage was not set up for this wrapper')
        return self._bqstorage_client

    def assess_query(self, query: str) -> bool:
        """
        Assesses whether the query is valid or not. Logs the volume (in bytes) of data it would process.
        :param query: query to be executed
        :return: bool
        """
        LOGGER.info('Dry-running query...')
        job_config = bigquery.QueryJobConfig()
        job_config.dry_run = True
        job_config.use_query_cache = False
        try:
            query_job = self.client.query(query, job_config=job_config)
        except BadRequest as e:
            LOGGER.error(f'Query is not valid: \n{str(e)}')
            return False
        else:
            LOGGER.info(f'Query is valid. It would process {format_size(query_job.total_bytes_processed)}')
            return True

    def run_query(self, query: str, output_type: Union[str, None] = 'df', timeout: Optional[int] = None,
                  tags: Optional[dict] = None, use_query_cache: bool = True, use_progress_bar: bool = True,
                  use_bq_storage_api: bool = True) -> Union[pd.DataFrame, None]:
        """
        Runs a query and returns the output in the specified format
        :param query: query to be executed
        :param output_type: output type of the run_query function. One of ['df', None]. Defaults to 'df'
        :param timeout: maximum allowed for query to run (in seconds). If None, no timeout is set
        :param tags: dictionary with "type", "category" and "sub_category" keys to handle query tagging,
            e.g. {'type': 'reporting', 'category': 'tableau-folder', 'sub_category': 'workbook-name'}
        :param use_query_cache: whether to use query's cached results when queried tables have not changed
        :param use_progress_bar: whether to use a tqdm progress bar during fetching. Defaults to True
        :param use_bq_storage_api: whether to use BigQuery Storage API to speed up fetching output. Defaults to True
        :return: results in the chosen output_type
        """
        # If tags are specified, add header to query
        query = self._add_tags(query, tags)
        # Start query run
        LOGGER.info('Running query...')
        query_job = self._start_query(query, use_query_cache=use_query_cache)
        # Wait during query execution
        query_job = self._wait_until_finished(query_job, timeout)
        # Get query output
        results = self._fetch_output(query_job, output_type, use_progress_bar, use_bq_storage_api)
        LOGGER.info(f'Query processed: {format_size(query_job.total_bytes_processed)}')
        return results

    @staticmethod
    def _add_tags(query: str, tags: Optional[dict] = None) -> str:
        if tags:
            head = f"/* type='{tags['type']}', category='{tags['category']}', sub_category='{tags['sub_category']}' */"
            return head + '\n' + query
        return query

    def _start_query(self, query: str, use_query_cache: bool = True, to_table: Optional[str] = None,
                     partition_by: Optional[str] = None, if_exists: str = 'fail') -> JobType:
        job_config = bigquery.QueryJobConfig()
        if not use_query_cache:
            job_config.use_query_cache = False
        if to_table:
            _, dataset, table = self._parse_table_reference(to_table)
            job_config.destination = self.client.dataset(dataset).table(table)
            job_config.write_disposition = self._get_write_disposition(if_exists)
            if partition_by:
                job_config = self._add_partitioning(job_config, partition_by)
        else:
            if partition_by:
                raise BigQueryError('Argument "partition_by" can only be used when "to_table" is provided')
        return self.client.query(query, job_config=job_config)

    @staticmethod
    def _get_write_disposition(if_exists: str) -> str:
        if if_exists == 'fail':
            return bigquery.WriteDisposition.WRITE_EMPTY
        elif if_exists == 'append':
            return bigquery.WriteDisposition.WRITE_APPEND
        elif if_exists == 'replace':
            return bigquery.WriteDisposition.WRITE_TRUNCATE
        else:
            raise NotImplementedError('"if_exists" argument must be in ("fail", "append", "replace")')

    def _parse_table_reference(self, table_reference: str) -> Tuple:
        table_reference_split = table_reference.split('.')
        if len(table_reference_split) == 2:
            return self.client.project, table_reference_split[0], table_reference_split[1]
        elif len(table_reference_split) == 3:
            return tuple(table_reference_split)
        else:
            raise ValueError('Table ref must be in format: "dataset_id.table_id" or "project_id.dataset_id.table_name"')

    @staticmethod
    def _parse_table_schema(table_schema: dict) -> list:
        return [bigquery.SchemaField(column_name, bq_type) for column_name, bq_type in table_schema.items()]

    @staticmethod
    def _add_partitioning(job_config, partition_by):
        job_config.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field=partition_by
        )
        return job_config

    @staticmethod
    def _wait_until_finished(query_job: JobType, timeout: Optional[int] = None) -> JobType:
        with timeit(text='Query run took:', logger=LOGGER):
            try:
                query_job.result(timeout=timeout)  # Raises when errored or timed out
            except GoogleAPIError as exception:
                raise BigQueryError(exception.errors[0]['message']) from exception
        return query_job

    def _fetch_output(self, query_job: JobType, output_type: str, use_progress_bar: bool = True,
                      use_bq_storage_api: bool = True) -> Union[pd.DataFrame, None]:
        if output_type is None:
            return None
        elif output_type == 'df':
            result = query_job.result()
            with timeit(text=f'Fetching output "df" took:', logger=LOGGER):
                params = {}
                if use_progress_bar:
                    params['progress_bar_type'] = 'tqdm'
                if use_bq_storage_api:
                    params['bqstorage_client'] = self.bqstorage_client
                df = result.to_arrow(**params).to_pandas()
                LOGGER.info(f'Output "df" will take {format_size(df.memory_usage().sum())} in memory')
                return df
        else:
            raise NotImplementedError('Argument output_type must be in: ["df", None]')

    @timeit(text='Uploading df to table took:', logger=LOGGER)
    def to_table_from_df(self, df: pd.DataFrame, table_reference: str, if_exists: str = 'fail',
                         chunksize: Optional[int] = None, use_progress_bar: bool = True) -> None:
        """
        Uploads a DataFrame to a BigQuery table and creates it if it does not exist yet.
        :param df: pandas DataFrame to upload to BigQuery
        :param table_reference: reference of the table to create/append/replace (e.g. "warehouse.trip_fill" or
            "bbc-data-platform.warehouse.trip_fill")
        :param if_exists: action to take if the table already exists. Should be in ('fail', 'append', 'replace')
        :param chunksize: number of rows to be inserted in each chunk from the dataframe. Defaults to None, which loads
            the whole dataframe at once
        :param use_progress_bar: whether to use a tqdm progress bar during fetching. Defaults to True
        :return: None
        """
        LOGGER.info(f'Uploading df to {table_reference}...')
        project, dataset, table = self._parse_table_reference(table_reference)
        df.to_gbq(f'{dataset}.{table}', project_id=project, if_exists=if_exists, chunksize=chunksize,
                  progress_bar=use_progress_bar, credentials=self.client._credentials)

    @timeit(text='Running query and storing results into table took:', logger=LOGGER)
    def to_table_from_query(self, query: str, table_reference: Optional[str] = None, if_exists: str = 'fail',
                            tags: Optional[dict] = None, use_query_cache: bool = True,
                            partition_by: Optional[str] = None) -> None:
        """
        Run a query and load its result into a table.
        :param query: query to be executed
        :param table_reference: reference of the table to create/append/replace (e.g. "dataset_id.table_name" or
            "project_id.dataset_id.table_name")
        :param if_exists: behaviour to adopt when uploading results to BigQuery. Ignored when `to_table` is not
            provided. If provided, must be in ('fail', 'append', 'replace'). Defaults to 'fail'
        :param tags: dictionary with "type", "category" and "sub_category" keys to handle query tagging,
            e.g. {'type': 'reporting', 'category': 'tableau-folder', 'sub_category': 'workbook-name'}
        :param use_query_cache: whether to use query's cached results when queried tables have not changed
        :param partition_by: name of the date column on which to partition the created table by
        :return: None
        """
        # If tags are specified, add header to query
        query = self._add_tags(query, tags)
        # Run the query and load its result to a table
        LOGGER.info('Running query...')
        query_job = self._start_query(query, use_query_cache, to_table=table_reference, if_exists=if_exists,
                                      partition_by=partition_by)
        # Wait until query is finished
        self._wait_until_finished(query_job)  # Raises when errored
        LOGGER.info(f'Query processed: {format_size(query_job.total_bytes_processed)}')

    @timeit(text='Loading GCS data to BigQuery took:', logger=LOGGER)
    def to_table_from_gcs(self, source_gcs_uri: str, table_reference: str, source_type: str = 'csv',
                          if_exists: str = 'fail', table_schema: Optional[dict] = None,
                          partition_by: Optional[str] = None) -> None:
        """
        Load one or more GCS file(s) in BigQuery.
        :param source_gcs_uri: URI to  the file(s) to be loaded in BigQuery, e.g. 'gs://bucket_name/file_part_*.csv'.
            Compression in gzip is inferred from files and supported.
        :param table_reference: reference of the table to create/append/replace (e.g. "dataset_id.table_name" or
            "project_id.dataset_id.table_name")
        :param source_type: type of the files to be loaded in BigQuery. Must be in ("csv", "json"). Defaults to 'csv'
        :param if_exists: behaviour to adopt when uploading results to BigQuery. Ignored when `to_table` is not
            provided. If provided, must be in ('fail', 'append', 'replace'). Defaults to 'fail'
        :param table_schema: optional dictionary mapping the column names to be used to their associated BigQuery type,
            e.g. {'col_1': 'STRING', 'col_2': 'INT64', 'col_3': 'TIMESTAMP'}
        :param partition_by: name of the date column on which to partition the created table by
        :return: None
        """
        # Parse table reference
        project, dataset, table = self._parse_table_reference(table_reference)
        destination_table = bigquery.DatasetReference(project, dataset).table(table)
        # Create job config
        job_config = bigquery.LoadJobConfig()
        job_config.write_disposition = self._get_write_disposition(if_exists)
        # Handle table schema
        if table_schema:
            job_config.schema = self._parse_table_schema(table_schema)
        else:
            job_config.autodetect = True
        # Handle partitioning
        if partition_by is not None:
            job_config = self._add_partitioning(job_config, partition_by)
        # Handle source format
        if source_type == 'csv':
            job_config.source_format = bigquery.SourceFormat.CSV
            if table_schema:
                job_config.skip_leading_rows = 1
        elif source_type == 'json':
            job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        else:
            raise NotImplementedError('Argument source_type must be in: ["csv", "json"]')
        # Start table load job
        load_job = self.client.load_table_from_uri(source_gcs_uri, destination_table, job_config=job_config)
        LOGGER.info(f'Loading CSV from {source_gcs_uri} to {table_reference}')
        # Wait for table load to complete
        self._wait_until_finished(load_job)  # Raises when errored
