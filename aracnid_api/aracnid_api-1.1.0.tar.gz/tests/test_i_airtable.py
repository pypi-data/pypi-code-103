"""Test functions for Airtable interface functionality.
"""
from datetime import datetime
import os

import airtable
import pytest

from aracnid_api import AirtableInterface


DATETIME_TEST_STR = '2020-08-05T12:00:00-04:00'

@pytest.fixture(name='air')
def fixture_airtable():
    """Pytest fixture to initialize and return the AirtableInterface object.
    """
    base_id = os.environ.get('AIRTABLE_TEST_BASE_ID')
    return AirtableInterface(base_id=base_id)

def test_init_airtable(air):
    """Test that Airtable Interface was imported successfully.
    """
    assert air

def test_get_table(air):
    """Tests retrieving table.
    """
    table_name = 'test_date'
    table = air.get_table(table_name=table_name)

    assert table
    assert isinstance(table, airtable.airtable.Airtable)

def test_get_airtable_datetime(air):
    """Tests the datetime processing of Airtable Interface.
    """
    table_name = 'test_date'
    table = air.get_table(table_name=table_name)

    record_id = 'recuaPzY7QvSbysW1'
    record = table.get(record_id)

    assert record
    dtetime = air.get_airtable_datetime(record, 'datetime_field')
    assert dtetime.isoformat() == DATETIME_TEST_STR

def test_get_airtable_datetime_createdTime(air):
    """Tests the datetime processing of Airtable Interface.
    """
    table_name = 'test_date'
    table = air.get_table(table_name=table_name)

    record_id = 'recuaPzY7QvSbysW1'
    record = table.get(record_id)

    assert record
    dtetime = air.get_airtable_datetime(record, 'createdTime')
    assert type(dtetime) is datetime

def test_match_record(air):
    """Tests matching an airtable record.
    """
    record_id = 'recuaPzY7QvSbysW1'

    table_name = 'test_date'
    table = air.get_table(table_name=table_name)

    field_name='name'
    field_value="test_record"
    record = air.match_record(table, field_name=field_name, field_value=field_value)

    assert record
    assert record['id'] == record_id

def test_match_record_with_apostrophes(air):
    """Tests matching an airtable record.
    """
    record_id = 'recnWXHPUSw0uXJRe'

    table_name = 'test_date'
    table = air.get_table(table_name=table_name)

    field_name='name'
    field_value="apostrophe's test"
    record = air.match_record(table, field_name=field_name, field_value=field_value)

    assert record
    assert record['id'] == record_id
