"""Class module to interface with Airtable.
"""
import os

from airtable import Airtable
from aracnid_logger import Logger
from dateutil.parser import parse


# initialize logging
logger = Logger(__name__).get_logger()


class AirtableInterface:
    """Airtable interface class.

    Environment Variables:
        AIRTABLE_API_KEY: Airtable API key.

    Attributes:
        air_api_key: The Airtable API key.
        base_id: The identifier of the Airtable base.

    Exceptions:
        None.
    """
    def __init__(self, base_id):
        """Initializes the interface with the base ID and the table name.

        Args:
            base_id: The identifier of the Airtable base.
        """
        # read environment variables
        self.air_api_key = os.environ.get('AIRTABLE_API_KEY')

        # set the base id for the interface
        self.base_id = base_id

    def get_table(self, table_name):
        """Returns the specified Airtable table.

        Args:
            table_name: The name of the table in the Airtable Base.
        """
        table = Airtable(self.base_id, table_name, self.air_api_key)

        return table

    @staticmethod
    def get_airtable_value(
        record, field_name, default=None, supress_warnings=False):
        """Retrieves the value from an Airtable record field.

        Args:
            record: The Airtable record.
            field_name: The name of the record's field.
            default: The default value of the field.
            supress_warnings: Flag to turn off warnings.
        """
        field_val = default
        if record:
            if field_name in record:
                field_val = record[field_name]

            elif field_name in record['fields']:
                field_val = record['fields'][field_name]

            if isinstance(field_val, list):
                if len(field_val) == 1:
                    field_val = field_val[0]
                else:
                    if not supress_warnings:
                        logger.warning(f'{field_name} has multiple values: '
                            f'{field_val}')

        return field_val

    @staticmethod
    def get_airtable_list(record, field_name, default=None):
        """Retrieves a list from an Airtable record field.

        Args:
            record: The Airtable record.
            field_name: The name of the record's field.
            default: The default value of the field.
        """
        field_val = default
        if field_name in record['fields']:
            field_val = record['fields'][field_name]

        return field_val

    @classmethod
    def get_airtable_datetime(
        cls, record, field_name, default=None, supress_warnings=False):
        """Retrieves a datetime value from an Airtable record field.

        The datetime value is localized.

        Args:
            record: The Airtable record.
            field_name: The name of the record's field.
            default: The default value of the field.
            supress_warnings: Flag to turn off warnings.
        """
        field_val = cls.get_airtable_value(
            record, field_name, default, supress_warnings)
        dt_local = parse(field_val).astimezone()

        return dt_local

    @classmethod
    def match_record(cls, table, field_name, field_value):
        """Returns a record that matches the specified field name and value.

        Tried using the .match() method, but this failed when apostrophes are passed.
        I updated the source code for C:\\Users\\Public\\Documents\\dev\\virtualenvs\\labdb\\Lib\\site-packages\\airtable\\params.py
        I updated line 210 to the following, swapping the quotes around.
        field_value = '"{}"'.format(field_value)
        This will work for apostrophes now, but will fail on double quotes.

        Args:
            table: The Airtable Table object.
            field_name: The name of the record's field.
            field_value: The value of the field.
        """
        record = None

        field_value_escaped = field_value.replace("'", r"\'")
        record = table.match(field_name, field_value_escaped)

        return record
