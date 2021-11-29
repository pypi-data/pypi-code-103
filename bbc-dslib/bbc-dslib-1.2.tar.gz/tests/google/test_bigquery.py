import logging
import re
from contextlib import contextmanager
from os import path
from queue import Queue
from uuid import uuid4

import mock
import pandas as pd
import pytest
from google.cloud import bigquery
from google.cloud.bigquery_storage import BigQueryReadClient
from pandas_gbq.gbq import TableCreationError
from testfixtures import LogCapture

from conftest import PROJECT_ID, TEMP_DATASET, TEMP_BUCKET, temp_files_to_gcs
from dslib import utils
from dslib.google import BigQueryWrapper, BigQueryError


# HELPERS

INVALID_QUERY = 'SELECT count(*) FROM'
TRIVIAL_QUERY = 'SELECT 1'
SELECT_QUERY = 'SELECT col_1, col_2 FROM {table_ref} ORDER BY 1,2;'
LOG_NO_BYTE_WILL_BE_READ = ('dslib.google._bigquery', 'INFO', 'Query is valid. It would process 0 bytes')
LOG_NO_BYTE_READ = ('dslib.google._bigquery', 'INFO', 'Query processed: 0 bytes')


def generate_temp_table_ref() -> str:
    return f'{TEMP_DATASET}.test_dslib_{str(uuid4())[-10:]}'


@contextmanager
def temp_table_ref(client: bigquery.Client) -> str:
    table_ref = generate_temp_table_ref()
    try:
        yield table_ref
    finally:
        client.delete_table(table_ref, not_found_ok=True)


def generate_temp_filename_template() -> str:
    return f'test_dslib_{str(uuid4())[-10:]}_part{{part}}.{{extension}}'


# FIXTURES

@pytest.fixture(scope='module')
def df():
    return pd.DataFrame({'col_1': [1, 2, 3], 'col_2': ['a', 'b', 'c']})


@pytest.fixture(scope='module')
def df_schema():
    return {'col_1': 'INT64', 'col_2': 'STRING'}


@pytest.fixture(scope='module')
def bigquery_client():
    return bigquery.Client(PROJECT_ID)


@pytest.fixture(scope='module')
def bq_storage_client():
    return BigQueryReadClient()


@pytest.fixture(scope='module')
def bq(bigquery_client, bq_storage_client):
    return BigQueryWrapper(bigquery_client, bq_storage_client)


@pytest.fixture(scope='function')
def nonexistent_table_ref(bigquery_client):
    with temp_table_ref(bigquery_client) as table_ref:
        yield table_ref


@pytest.fixture(scope='function')
def temporary_table_ref(bigquery_client, df):
    with temp_table_ref(bigquery_client) as table_ref:
        df.to_gbq(table_ref, project_id=PROJECT_ID, progress_bar=False, if_exists='fail')
        yield table_ref


@pytest.fixture(scope='module')
def persistent_table_ref(bigquery_client, df):
    with temp_table_ref(bigquery_client) as table_ref:
        df.to_gbq(table_ref, project_id=PROJECT_ID, progress_bar=False, if_exists='fail')
        yield table_ref


@pytest.fixture(scope='module')
def persistent_filename_template(df, storage_client):
    local_dirpath = utils.get_tmp_dirpath()
    filename_template = generate_temp_filename_template()
    filenames = []
    # Generate local CSV files
    for i in range(2):
        filename = filename_template.format(part=i, extension='csv')
        df.to_csv(path.join(local_dirpath, filename), index=False)
        filenames.append(filename)
    # Generate local JSON files
    for i in range(2):
        filename = filename_template.format(part=i, extension='json')
        df.to_json(path.join(local_dirpath, filename), orient="records", lines=True)
        filenames.append(filename)
    # Upload all files to GCS
    with temp_files_to_gcs(storage_client, TEMP_BUCKET, local_dirpath, filenames):
        yield filename_template


# TESTS

class TestInit:

    def test_init_from_params(self):
        # Act
        bq = BigQueryWrapper.from_params(PROJECT_ID)
        # Assert
        assert 'client' in bq.__dict__.keys()
        assert bq.client.__class__ == bigquery.Client

    def test_init_no_bq_storage(self, bigquery_client):
        # Act
        bq = BigQueryWrapper(bigquery_client)
        # Assert
        assert 'client' in bq.__dict__.keys()
        assert bq.client.__class__ == bigquery.Client
        with pytest.raises(BigQueryError, match='BigQuery Storage was not set up'):
            print(bq.bqstorage_client.__class__)

    def test_init_from_params_no_bq_storage(self):
        # Act
        bq = BigQueryWrapper.from_params(PROJECT_ID, setup_bqstorage=False)
        # Assert
        assert 'client' in bq.__dict__.keys()
        assert bq.client.__class__ == bigquery.Client
        with pytest.raises(BigQueryError, match='BigQuery Storage was not set up'):
            print(bq.bqstorage_client.__class__)

    def test_init_invalid(self):
        # Assert
        with pytest.raises(ValueError):
            BigQueryWrapper(PROJECT_ID)


class TestAssessQuery:

    def test_invalid(self, bq):
        # Assert
        assert bq.assess_query(INVALID_QUERY) is False

    def test_valid(self, bq):
        # Assert
        with LogCapture(level=logging.INFO) as logs:
            assert bq.assess_query(TRIVIAL_QUERY) is True
        logs.check_present(LOG_NO_BYTE_WILL_BE_READ)


class TestRunQuery:

    def test_invalid(self, bq):
        # Assert
        with pytest.raises(BigQueryError):
            bq.run_query(INVALID_QUERY)

    def test_output_type_unknown(self, bq):
        # Assert
        with pytest.raises(NotImplementedError):
            bq.run_query(TRIVIAL_QUERY, output_type='junk')

    def test_output_type_df(self, bq, persistent_table_ref, df):
        # Arrange
        query = SELECT_QUERY.format(table_ref=persistent_table_ref)
        # Act
        result = bq.run_query(query, output_type='df')
        # Assert
        assert df.equals(result)

    def test_output_type_none(self, bq):
        # Act
        result = bq.run_query(TRIVIAL_QUERY, output_type=None)
        # Assert
        assert result is None

    def test_cache(self, bq, persistent_table_ref):
        # Arrange
        query = SELECT_QUERY.format(table_ref=persistent_table_ref)
        bq.run_query(query, output_type=None)  # Run it a first time to have it in the cache
        # Act
        with LogCapture(level=logging.INFO) as logs:
            bq.run_query(query, output_type=None, use_query_cache=True)
        # Assert
        logs.check_present(LOG_NO_BYTE_READ)

    def test_no_cache(self, bq, persistent_table_ref):
        # Arrange
        query = SELECT_QUERY.format(table_ref=persistent_table_ref)
        # Act
        bq.run_query(query, output_type=None)  # Run it a first time to have it in the cache
        with LogCapture(level=logging.INFO) as logs:
            bq.run_query(query, output_type=None, use_query_cache=False)
        # Assert
        with pytest.raises(AssertionError):
            logs.check_present(LOG_NO_BYTE_READ)

    def test_add_tags(self, bq):
        # Arrange
        queue = Queue()

        def mock_start_query(query, *args, **kwargs):
            query_job = BigQueryWrapper._start_query(bq, query, *args, **kwargs)
            queue.put(query_job.query)
            return query_job

        # Act
        with mock.patch.object(bq, '_start_query', side_effect=mock_start_query):
            bq.run_query(TRIVIAL_QUERY, output_type=None, tags={'type': 'junk', 'category': 'junk', 'sub_category': 'junk'})

        # Assert
        executed_query = queue.get()
        pattern = re.compile(r"/\* type='.*', category='.*', sub_category='.*' \*/")
        assert pattern.match(executed_query) is not None


class TestToTableFromDf:

    def test_existing_table(self, df, bq, persistent_table_ref):
        # Assert
        with pytest.raises(TableCreationError):
            bq.to_table_from_df(df, persistent_table_ref, if_exists='fail')

    def test_create_table(self, df, bq, nonexistent_table_ref):
        # Act
        bq.to_table_from_df(df, nonexistent_table_ref)
        expected_df = df
        # Assert
        actual_df = bq.run_query(SELECT_QUERY.format(table_ref=nonexistent_table_ref))
        assert expected_df.equals(actual_df)

    def test_append_table(self, df, bq, temporary_table_ref):
        # Arrange
        expected_df = pd.concat([df, df], axis=0).sort_values(['col_1', 'col_2']).reset_index(drop=True)
        # Act
        bq.to_table_from_df(df, temporary_table_ref, if_exists='append')
        # Assert
        actual_df = bq.run_query(SELECT_QUERY.format(table_ref=temporary_table_ref))
        assert expected_df.equals(actual_df)

    def test_replace_table(self, df, bq, temporary_table_ref):
        # Arrange
        expected_df = df.copy()
        expected_df['col_1'] = df['col_1'] + 1
        # Act
        bq.to_table_from_df(expected_df, temporary_table_ref, if_exists='replace')
        # Assert
        actual_df = bq.run_query(SELECT_QUERY.format(table_ref=temporary_table_ref))
        assert expected_df.equals(actual_df)

    def test_invalid_reference(self, bq):
        # Assert
        with pytest.raises(ValueError, match='Table ref must be in format'):
            bq.to_table_from_df(df, 'junk')

    def test_long_reference(self, df, bq, nonexistent_table_ref):
        # Arrange
        long_table_ref_wrapper = f'{PROJECT_ID}.{nonexistent_table_ref}'
        long_table_ref_bq = f'`{PROJECT_ID}`.{nonexistent_table_ref}'
        expected_df = df
        # Act
        bq.to_table_from_df(df, long_table_ref_wrapper)
        # Assert
        actual_df = bq.run_query(SELECT_QUERY.format(table_ref=long_table_ref_bq))
        assert expected_df.equals(actual_df)


class TestToTableFromQuery:

    def test_existing_table(self, bq, persistent_table_ref):
        # Arrange
        select_query = SELECT_QUERY.format(table_ref=persistent_table_ref)
        # Assert
        with pytest.raises(BigQueryError, match='Already Exists'):
            bq.to_table_from_query(select_query, persistent_table_ref, if_exists='fail')

    def test_create_table(self, bq, df, persistent_table_ref, nonexistent_table_ref):
        # Arrange
        select_query = SELECT_QUERY.format(table_ref=persistent_table_ref)
        expected_df = df
        # Act
        bq.to_table_from_query(select_query, nonexistent_table_ref)
        # Assert
        actual_df = bq.run_query(SELECT_QUERY.format(table_ref=nonexistent_table_ref))
        assert expected_df.equals(actual_df)

    def test_append_table(self, df, bq, temporary_table_ref):
        # Arrange
        expected_df = pd.concat([df, df], axis=0).sort_values(['col_1', 'col_2']).reset_index(drop=True)
        select_query = SELECT_QUERY.format(table_ref=temporary_table_ref)
        # Act
        bq.to_table_from_query(select_query, temporary_table_ref, if_exists='append')
        # Assert
        actual_df = bq.run_query(select_query)
        assert expected_df.equals(actual_df)

    def test_replace_table(self, df, bq, temporary_table_ref):
        # Arrange
        expected_df = df.copy()
        expected_df['col_1'] = df['col_1'] + 1
        query = f'SELECT col_1 + 1 AS col_1, col_2 FROM {temporary_table_ref} ORDER BY 1, 2'
        # Act
        bq.to_table_from_query(query, temporary_table_ref, if_exists='replace')
        # Assert
        actual_df = bq.run_query(SELECT_QUERY.format(table_ref=temporary_table_ref))
        assert expected_df.equals(actual_df)

    def test_unknown_if_exists(self, bq, nonexistent_table_ref):
        # Assert
        with pytest.raises(NotImplementedError, match='"if_exists" argument must be in'):
            bq.to_table_from_query(TRIVIAL_QUERY, nonexistent_table_ref, if_exists='junk')

    def test_invalid_reference(self, bq):
        # Assert
        with pytest.raises(ValueError, match='Table ref must be in format'):
            bq.to_table_from_query(TRIVIAL_QUERY, 'junk')

    def test_long_reference(self, df, bq, persistent_table_ref, nonexistent_table_ref):
        # Arrange
        long_table_ref_wrapper = f'{PROJECT_ID}.{nonexistent_table_ref}'
        long_table_ref_bq = f'`{PROJECT_ID}`.{nonexistent_table_ref}'
        expected_df = df
        # Act
        bq.to_table_from_query(SELECT_QUERY.format(table_ref=persistent_table_ref), long_table_ref_wrapper)
        actual_df = bq.run_query(SELECT_QUERY.format(table_ref=long_table_ref_bq))
        # Assert
        assert expected_df.equals(actual_df)

    def test_partitioning(self, bq, persistent_table_ref, nonexistent_table_ref):
        # Arrange
        query = f"SELECT *, DATE('2021-02-12') AS part_date FROM {persistent_table_ref}"
        # Act
        bq.to_table_from_query(query, nonexistent_table_ref, partition_by='part_date')
        # Assert
        table = bq.client.get_table(nonexistent_table_ref)
        assert table.partitioning_type == 'DAY'
        assert table.time_partitioning.field == 'part_date'


class TestToTableFromGcs:

    types = ['csv', 'json']

    @pytest.mark.parametrize('source_type', types)
    def test_existing_table(self, bq, persistent_filename_template, persistent_table_ref, source_type):
        # Arrange
        source_file = f"gs://{TEMP_BUCKET}/{persistent_filename_template.format(extension=source_type, part=1)}"
        # Assert
        with pytest.raises(BigQueryError, match='Already Exists'):
            bq.to_table_from_gcs(source_file, persistent_table_ref, source_type=source_type, if_exists='fail')

    @pytest.mark.parametrize('source_type', types)
    def test_create_table(self, bq, df, persistent_filename_template, nonexistent_table_ref, source_type):
        # Arrange
        source_file = f"gs://{TEMP_BUCKET}/{persistent_filename_template.format(extension=source_type, part=1)}"
        expected_df = df
        # Act
        bq.to_table_from_gcs(source_file, nonexistent_table_ref, source_type=source_type, if_exists='fail')
        # Assert
        actual_df = bq.run_query(SELECT_QUERY.format(table_ref=nonexistent_table_ref))
        assert expected_df.equals(actual_df)

    @pytest.mark.parametrize('source_type', types)
    def test_append_table(self, bq, df, persistent_filename_template, temporary_table_ref, source_type):
        # Arrange
        source_file = f"gs://{TEMP_BUCKET}/{persistent_filename_template.format(extension=source_type, part=1)}"
        expected_df = pd.concat([df, df], axis=0).sort_values(['col_1', 'col_2']).reset_index(drop=True)
        # Act
        bq.to_table_from_gcs(source_file, temporary_table_ref, source_type=source_type, if_exists='append')
        # Assert
        actual_df = bq.run_query(SELECT_QUERY.format(table_ref=temporary_table_ref))
        assert expected_df.equals(actual_df)

    @pytest.mark.parametrize('source_type', types)
    def test_replace_table(self, bq, df, persistent_filename_template, temporary_table_ref, source_type):
        # Arrange
        source_file = f"gs://{TEMP_BUCKET}/{persistent_filename_template.format(extension=source_type, part=1)}"
        expected_df = df
        # Act
        bq.to_table_from_gcs(source_file, temporary_table_ref, source_type=source_type, if_exists='replace')
        # Assert
        actual_df = bq.run_query(SELECT_QUERY.format(table_ref=temporary_table_ref))
        assert expected_df.equals(actual_df)

    def test_unknown_if_exists(self, bq, persistent_filename_template, nonexistent_table_ref):
        # Arrange
        source_file = f"gs://{TEMP_BUCKET}/{persistent_filename_template.format(extension='csv', part=1)}"
        # Assert
        with pytest.raises(NotImplementedError, match='"if_exists" argument must be in'):
            bq.to_table_from_gcs(source_file, nonexistent_table_ref, source_type='csv', if_exists='junk')

    def test_invalid_reference(self, bq, persistent_filename_template):
        # Arrange
        source_file = f"gs://{TEMP_BUCKET}/{persistent_filename_template.format(extension='csv', part=1)}"
        # Assert
        with pytest.raises(ValueError, match='Table ref must be in format'):
            bq.to_table_from_gcs(source_file, 'junk', source_type='csv')

    def test_long_reference(self, bq, df, persistent_filename_template, nonexistent_table_ref):
        # Arrange
        source_file = f"gs://{TEMP_BUCKET}/{persistent_filename_template.format(extension='csv', part=1)}"
        long_table_ref_wrapper = f'{PROJECT_ID}.{nonexistent_table_ref}'
        long_table_ref_bq = f'`{PROJECT_ID}`.{nonexistent_table_ref}'
        expected_df = df
        # Act
        bq.to_table_from_gcs(source_file, long_table_ref_wrapper)
        actual_df = bq.run_query(SELECT_QUERY.format(table_ref=long_table_ref_bq))
        # Assert
        assert expected_df.equals(actual_df)

    @pytest.mark.parametrize('source_type', types)
    def test_multiple_files(self, bq, df, persistent_filename_template, nonexistent_table_ref, source_type):
        # Arrange
        source_file = f"gs://{TEMP_BUCKET}/{persistent_filename_template.format(extension=source_type, part='*')}"
        expected_df = pd.concat([df, df], axis=0, ignore_index=True).sort_values('col_1').reset_index(drop=True)
        # Act
        bq.to_table_from_gcs(source_file, nonexistent_table_ref, source_type=source_type)
        # Assert
        result = bq.run_query(SELECT_QUERY.format(table_ref=nonexistent_table_ref))
        assert expected_df.equals(result)

    @pytest.mark.parametrize('source_type', types)
    def test_schema(self, bq, df, df_schema, persistent_filename_template, nonexistent_table_ref, source_type):
        # Arrange
        source_file = f"gs://{TEMP_BUCKET}/{persistent_filename_template.format(extension=source_type, part=1)}"
        expected_df = df
        # Act
        bq.to_table_from_gcs(source_file, nonexistent_table_ref, source_type, table_schema=df_schema)
        actual_df = bq.run_query(SELECT_QUERY.format(table_ref=nonexistent_table_ref))
        # Assert
        assert expected_df.equals(actual_df)

    def test_invalid_source_type(self, bq, persistent_filename_template, nonexistent_table_ref):
        # Arrange
        source_file = f"gs://{TEMP_BUCKET}/{persistent_filename_template.format(extension='junk', part=1)}"
        # Assert
        with pytest.raises(NotImplementedError, match='must be in'):
            bq.to_table_from_gcs(source_file, nonexistent_table_ref, source_type='junk', if_exists='fail')

    def test_partitioning(self, storage_client, bq, df, nonexistent_table_ref):
        # Arrange
        local_dirpath = utils.get_tmp_dirpath()
        filename = generate_temp_filename_template().format(part=1, extension='csv')
        df_with_date = df.copy()
        df_with_date['part_date'] = '2021-02-12'
        df_with_date.to_csv(path.join(local_dirpath, filename), index=False)
        # Act
        with temp_files_to_gcs(storage_client, TEMP_BUCKET, local_dirpath, [filename]):
            bq.to_table_from_gcs(f'gs://{TEMP_BUCKET}/{filename}', nonexistent_table_ref, partition_by='part_date')
        # Assert
        table = bq.client.get_table(nonexistent_table_ref)
        assert table.partitioning_type == 'DAY'
        assert table.time_partitioning.field == 'part_date'
