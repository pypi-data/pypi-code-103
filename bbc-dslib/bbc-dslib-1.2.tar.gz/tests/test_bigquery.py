import logging
import re
from contextlib import contextmanager
from os import path
from queue import Queue
from uuid import uuid4

import mock
import pandas as pd
import pytest
from google.api_core.exceptions import NotFound
from google.cloud import bigquery, storage
from google.cloud.bigquery_storage import BigQueryReadClient
from pandas_gbq.gbq import TableCreationError
from testfixtures import LogCapture

from dslib.utils import get_tmp_dirpath
from dslib.wrappers.google.bigquery import BigQueryWrapper, BigQueryError


# HELPERS ##############################################################################################################

PROJECT_ID = 'bbc-data-marketplace'
TEMP_DATASET = 'temp_1day'
TEMP_BUCKET = 'bbc-data-marketplace-temp1day'


def generate_temp_table_ref():
    return f'{TEMP_DATASET}.test_dslib_{str(uuid4())[-10:]}'


def generate_temp_file_ref():
    return f'test_dslib_{str(uuid4())[-10:]}_part{{part}}.{{extension}}'


@contextmanager
def create_temp_table(client, df):
    table_ref = generate_temp_table_ref()
    try:
        df.to_gbq(table_ref, project_id=PROJECT_ID, progress_bar=False, if_exists='fail')
        yield table_ref
    finally:
        client.delete_table(table_ref, not_found_ok=True)


# FIXTURES #############################################################################################################
# TODO: stop using fixtures, rather use setUp, setUpClass, tearDown, and tearDownClass methods

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
def temp_table_ref(bigquery_client, df):
    with create_temp_table(bigquery_client, df) as temp_table_ref:
        yield temp_table_ref


@pytest.fixture(scope='module')
def storage_client():
    return storage.Client(PROJECT_ID)


@pytest.fixture(scope='module')
def temp_files_ref(df, storage_client):
    filename = generate_temp_file_ref()
    dirpath = get_tmp_dirpath()
    filepaths = []
    # Generate local CSV files
    for i in range(2):
        filepath = filename.format(part=i, extension='csv')
        df.to_csv(path.join(dirpath, filepath), index=False)
        filepaths.append(filepath)
    # Generate local JSON files
    for i in range(2):
        filepath = filename.format(part=i, extension='json')
        df.to_json(path.join(dirpath, filepath), orient="records", lines=True)
        filepaths.append(filepath)
    # Upload all files to GCS
    bucket = storage_client.bucket(TEMP_BUCKET)
    for filepath in filepaths:
        blob = bucket.blob(filepath)
        with open(path.join(dirpath, filepath), 'rb') as fileobj:
            blob.upload_from_file(fileobj)
    return filename


# TESTS ################################################################################################################

def test_init_from_params():
    bq = BigQueryWrapper.from_params(PROJECT_ID)
    assert 'client' in bq.__dict__.keys()
    assert bq.client.__class__ == bigquery.Client


def test_init_no_bq_storage(bigquery_client):
    # TODO: For all of the tests: use the AAA framework (arrange, act, assert)
    bq = BigQueryWrapper(bigquery_client)
    assert 'client' in bq.__dict__.keys()
    assert bq.client.__class__ == bigquery.Client
    with pytest.raises(BigQueryError, match='BigQuery Storage was not set up'):
        print(bq.bqstorage_client.__class__)


def test_init_from_params_no_bq_storage():
    bq = BigQueryWrapper.from_params(PROJECT_ID, setup_bqstorage=False)
    assert 'client' in bq.__dict__.keys()
    assert bq.client.__class__ == bigquery.Client
    with pytest.raises(BigQueryError, match='BigQuery Storage was not set up'):
        print(bq.bqstorage_client.__class__)


def test_init_invalid():
    with pytest.raises(ValueError):
        BigQueryWrapper(PROJECT_ID)


class TestAssessQuery:

    def test_invalid(self, bq):
        assert bq.assess_query('SELECT count(*) FROM') is False

    def test_valid(self, bq, temp_table_ref):
        with LogCapture(level=logging.INFO) as logs:
            assert bq.assess_query(f'SELECT count(*) FROM {temp_table_ref}') is True
        logs.check_present(('dslib.wrappers.google.bigquery', 'INFO', 'Query is valid. It would process 0 bytes'))


class TestRunQuery:

    def test_invalid(self, bq):
        with pytest.raises(BigQueryError):
            bq.run_query('SELECT count(*) FROM')

    def test_output_type_unknown(self, bq, temp_table_ref):
        with pytest.raises(NotImplementedError):
            # TODO: f'SELECT * FROM {temp_table_ref}' is used quite often => to be put in a variable
            bq.run_query(f'SELECT * FROM {temp_table_ref}', output_type='junk')

    def test_output_type_df(self, bq, temp_table_ref, df):
        result = bq.run_query(f'SELECT * FROM {temp_table_ref};', output_type='df')
        assert df.equals(result)

    def test_output_type_none(self, bigquery_client, bq, temp_table_ref):
        result = bq.run_query(f'DROP TABLE {temp_table_ref};', output_type=None)
        assert result is None
        with pytest.raises(NotFound):
            bigquery_client.delete_table(temp_table_ref, not_found_ok=False)

    def test_no_cache(self, bq, temp_table_ref):
        # Run it a first time to have it in the cache
        bq.run_query(f'SELECT * FROM {temp_table_ref}', output_type=None)
        # Check with that cache is used with use_query_cache = True
        with LogCapture(level=logging.INFO) as logs:
            bq.run_query(f'SELECT * FROM {temp_table_ref}', output_type=None, use_query_cache=True)
        logs.check_present(('dslib.wrappers.google.bigquery', 'INFO', 'Query processed: 0 bytes'))
        # Check with that cache is not used with use_query_cache = False
        with LogCapture(level=logging.INFO) as logs:
            bq.run_query(f'SELECT * FROM {temp_table_ref}', output_type=None, use_query_cache=False)
        with pytest.raises(AssertionError, match='sequence not as expected'):
            logs.check_present(('dslib.wrappers.google.bigquery', 'INFO', 'Query processed: 0 bytes'))

    def test_add_tags(self, bq, temp_table_ref):
        query = f'SELECT * FROM {temp_table_ref};'
        queue = Queue()

        def mock_start_query(query, *args, **kwargs):
            queue.put(query)
            return BigQueryWrapper._start_query(bq, query, *args, **kwargs)

        with mock.patch.object(bq, '_start_query', side_effect=mock_start_query):
            bq.run_query(query, output_type=None, tags={'type': 'junk', 'category': 'junk', 'sub_category': 'junk'})

        query = queue.get()
        pattern = re.compile(r"/\* type='.*', category='.*', sub_category='.*' \*/")
        assert pattern.match(query) is not None


class TestToTableFromDf:

    def test_existing_table(self, df, bq, temp_table_ref):
        with pytest.raises(TableCreationError):
            bq.to_table_from_df(df, temp_table_ref, if_exists='fail')

    def test_create_table(self, df, bq):
        new_temp_table_ref = generate_temp_table_ref()  # We do not use the fixture here
        bq.to_table_from_df(df, new_temp_table_ref)
        result = bq.run_query(f'SELECT * FROM {new_temp_table_ref}')
        assert df.equals(result)

    def test_append_table(self, df, bq, temp_table_ref):
        # TODO: would be clearer if we detailed the expected df here: expected_df = pd.DataFrame({'col_1': [1, 2, 3...
        bq.to_table_from_df(df, temp_table_ref, if_exists='append')
        result = bq.run_query(f'SELECT * FROM {temp_table_ref}')
        assert pd.concat([df, df], axis=0, ignore_index=True).equals(result)

    def test_replace_table(self, df, bq, temp_table_ref):
        expected_df = df[['col_1']] + 1
        bq.to_table_from_df(expected_df, temp_table_ref, if_exists='replace')
        result = bq.run_query(f'SELECT * FROM {temp_table_ref}')
        assert expected_df.equals(result)

    def test_invalid_reference(self, bq, temp_table_ref):
        with pytest.raises(ValueError, match='Table ref must be in format'):
            bq.to_table_from_df(df, 'junk')

    def test_long_reference(self, df, bq):
        new_temp_table_ref = generate_temp_table_ref()  # We do not use the fixture here
        bq.to_table_from_df(df, f'{PROJECT_ID}.{new_temp_table_ref}')
        result = bq.run_query(f'SELECT * FROM `{PROJECT_ID}`.{new_temp_table_ref}')
        assert df.equals(result)


class TestToTableFromQuery:

    def test_existing_table(self, bq, temp_table_ref):
        with pytest.raises(BigQueryError, match='Already Exists'):
            bq.to_table_from_query(f'SELECT * FROM {temp_table_ref}', temp_table_ref, if_exists='fail')

    def test_create_table(self, bq, df, temp_table_ref):
        new_temp_table_ref = generate_temp_table_ref()  # We do not use the fixture here
        bq.to_table_from_query(f'SELECT * FROM {temp_table_ref} ORDER BY 1', new_temp_table_ref)
        result = bq.run_query(f'SELECT * FROM {new_temp_table_ref} ORDER BY 1')
        assert df.equals(result)

    def test_append_table(self, df, bq, temp_table_ref):
        bq.to_table_from_query(f'SELECT * FROM {temp_table_ref} ORDER BY 1', temp_table_ref, if_exists='append')
        result = bq.run_query(f'SELECT * FROM {temp_table_ref} ORDER BY 1')
        expected = pd.concat([df, df], axis=0, ignore_index=True).sort_values('col_1').reset_index(drop=True)
        assert expected.equals(result)

    def test_replace_table(self, df, bq, temp_table_ref):
        expected_df = df[['col_1']] + 1
        query = f'SELECT col_1 + 1 AS col_1 FROM {temp_table_ref} ORDER BY 1'
        bq.to_table_from_query(query, temp_table_ref, if_exists='replace')
        result = bq.run_query(f'SELECT * FROM {temp_table_ref} ORDER BY 1')
        assert expected_df.equals(result)

    def test_unknown_if_exists(self, bq, temp_table_ref):
        with pytest.raises(NotImplementedError, match='"if_exists" argument must be in'):
            bq.to_table_from_query(f'SELECT * FROM {temp_table_ref}', temp_table_ref, if_exists='junk')

    def test_invalid_reference(self, bq, temp_table_ref):
        with pytest.raises(ValueError, match='Table ref must be in format'):
            bq.to_table_from_query(f'SELECT * FROM {temp_table_ref}', 'junk')

    def test_long_reference(self, bq, df, temp_table_ref):
        new_temp_table_ref = generate_temp_table_ref()  # We do not use the fixture here
        bq.to_table_from_query(f'SELECT * FROM {temp_table_ref} ORDER BY 1', f'{PROJECT_ID}.{new_temp_table_ref}')
        result = bq.run_query(f'SELECT * FROM `{PROJECT_ID}`.{new_temp_table_ref} ORDER BY 1')
        assert df.equals(result)


class TestToTableFromGcs:

    types = ['csv', 'json']

    @pytest.mark.parametrize('source_type', types)
    def test_existing_table(self, bq, temp_files_ref, temp_table_ref, source_type):
        source_file = f"gs://{TEMP_BUCKET}/{temp_files_ref.format(extension=source_type, part=1)}"
        with pytest.raises(BigQueryError, match='Already Exists'):
            bq.to_table_from_gcs(source_file, temp_table_ref, source_type=source_type, if_exists='fail')

    @pytest.mark.parametrize('source_type', types)
    def test_create_table(self, bq, df, temp_files_ref, source_type):
        source_file = f"gs://{TEMP_BUCKET}/{temp_files_ref.format(extension=source_type, part=1)}"
        new_temp_table_ref = generate_temp_table_ref()  # We do not use the fixture here
        bq.to_table_from_gcs(source_file, new_temp_table_ref, source_type=source_type, if_exists='fail')
        result = bq.run_query(f'SELECT {",".join(df.columns)} FROM {new_temp_table_ref} ORDER BY 1')
        assert df.equals(result)

    @pytest.mark.parametrize('source_type', types)
    def test_append_table(self, bq, df, temp_files_ref, temp_table_ref, source_type):
        source_file = f"gs://{TEMP_BUCKET}/{temp_files_ref.format(extension=source_type, part=1)}"
        bq.to_table_from_gcs(source_file, temp_table_ref, source_type=source_type, if_exists='append')
        result = bq.run_query(f'SELECT {",".join(df.columns)} FROM {temp_table_ref}')
        assert pd.concat([df, df], axis=0, ignore_index=True).equals(result)

    @pytest.mark.parametrize('source_type', types)
    def test_replace_table(self, bq, df, temp_table_ref, temp_files_ref, source_type):
        source_file = f"gs://{TEMP_BUCKET}/{temp_files_ref.format(extension=source_type, part=1)}"
        bq.to_table_from_gcs(source_file, temp_table_ref, source_type=source_type, if_exists='replace')
        result = bq.run_query(f'SELECT {",".join(df.columns)} FROM {temp_table_ref} ORDER BY 1')
        assert df.equals(result)

    def test_unknown_if_exists(self, bq, temp_table_ref, temp_files_ref):
        source_file = f"gs://{TEMP_BUCKET}/{temp_files_ref.format(extension='csv', part=1)}"
        with pytest.raises(NotImplementedError, match='"if_exists" argument must be in'):
            bq.to_table_from_gcs(source_file, temp_table_ref, source_type='csv', if_exists='junk')

    def test_invalid_reference(self, bq, temp_files_ref):
        with pytest.raises(ValueError, match='Table ref must be in format'):
            source_file = f"gs://{TEMP_BUCKET}/{temp_files_ref.format(extension='csv', part=1)}"
            bq.to_table_from_gcs(source_file, 'junk', source_type='csv')

    def test_long_reference(self, bq, df, temp_files_ref, temp_table_ref):
        source_file = f"gs://{TEMP_BUCKET}/{temp_files_ref.format(extension='csv', part=1)}"
        bq.to_table_from_gcs(source_file, f'{PROJECT_ID}.{temp_table_ref}', if_exists='replace')
        result = bq.run_query(f'SELECT * FROM `{PROJECT_ID}.{temp_table_ref}` ORDER BY 1')
        assert df.equals(result)

    @pytest.mark.parametrize('source_type', types)
    def test_multiple_files(self, bq, df, temp_files_ref, temp_table_ref, source_type):
        source_file = f"gs://{TEMP_BUCKET}/{temp_files_ref.format(extension=source_type, part='*')}"
        bq.to_table_from_gcs(source_file, temp_table_ref, source_type=source_type, if_exists='replace')
        expected_df = pd.concat([df, df], axis=0, ignore_index=True).sort_values('col_1').reset_index(drop=True)
        result = bq.run_query(f'SELECT {",".join(df.columns)} FROM {temp_table_ref} ORDER BY 1')
        assert expected_df.equals(result)

    @pytest.mark.parametrize('source_type', types)
    def test_schema(self, bq, df, df_schema, temp_files_ref, source_type):
        source_file = f"gs://{TEMP_BUCKET}/{temp_files_ref.format(extension=source_type, part=1)}"
        new_temp_table_ref = generate_temp_table_ref()  # We do not use the fixture here
        bq.to_table_from_gcs(source_file, new_temp_table_ref, source_type, if_exists='fail', table_schema=df_schema)
        result = bq.run_query(f'SELECT {",".join(df.columns)} FROM {new_temp_table_ref} ORDER BY 1')
        assert df.equals(result)

    def test_invalid_source_type(self, bq, temp_files_ref):
        source_file = f"gs://{TEMP_BUCKET}/{temp_files_ref.format(extension='junk', part=1)}"
        new_temp_table_ref = generate_temp_table_ref()  # We do not use the fixture here
        with pytest.raises(NotImplementedError, match='must be in'):
            bq.to_table_from_gcs(source_file, new_temp_table_ref, source_type='junk', if_exists='fail')

