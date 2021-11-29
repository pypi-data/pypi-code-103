import logging
import os
import string
from itertools import islice
from typing import Optional

try:
    import gspread
    import pandas as pd
    from gspread_dataframe import set_with_dataframe
    from oauth2client.service_account import ServiceAccountCredentials
    from oauth2client.client import GoogleCredentials
except ImportError as e:
    raise ImportError('Please install "google" extra packages.') from e

LOGGER = logging.getLogger(__name__)


class SheetError(Exception):
    pass


def colname_generator():
    # First 26 colnames are ASCII uppercase characters
    for letter in string.ascii_uppercase:
        yield letter
    # Then it's AA, AB, AC, ..., BA, BB, BC, ...
    for letter_1 in string.ascii_uppercase:
        for letter_2 in string.ascii_uppercase:
            yield letter_1 + letter_2


class SpreadsheetWrapper(object):

    scopes = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

    def __init__(self, client: gspread.client.Client, default_spreadsheet_id: Optional[str] = None):
        if not client.__class__.__name__ == 'Client':
            raise ValueError('"client" argument must be a Google Spreadsheet "Client" instance')
        self.client = client
        self.default_spreadsheet_id = default_spreadsheet_id

    @classmethod
    def from_params(cls, default_spreadsheet_id: Optional[str] = None, auth_file: str = None):
        if auth_file:
            if not os.path.exists(auth_file):
                raise FileNotFoundError(f'Authentication file does not exist: {auth_file}')
            credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_file, scopes=cls.scopes)
        else:
            credentials = GoogleCredentials.get_application_default().create_scoped(cls.scopes)
        client = gspread.authorize(credentials)
        return cls(client, default_spreadsheet_id=default_spreadsheet_id)

    def _require_spreadsheet(self, spreadsheet_id: Optional[str] = None) -> gspread.Spreadsheet:
        spreadsheet_id = spreadsheet_id or self.default_spreadsheet_id
        if not spreadsheet_id:
            raise ValueError('You need to specify a bucket_name, either at wrapper level or function level')
        return self.client.open_by_key(spreadsheet_id)

    @staticmethod
    def _get_worksheet(spreadsheet: gspread.Spreadsheet, worksheet_title: str) -> gspread.Worksheet:
        if not worksheet_title:
            return spreadsheet.get_worksheet(0)
        else:
            return spreadsheet.worksheet(worksheet_title)

    @staticmethod
    def _get_nth_colname(n):
        return next(islice(colname_generator(), n, n+1))

    def worksheet_exists(self, worksheet_title: str, spreadsheet_id: Optional[str] = None) -> bool:
        """
        Check whether a specific worksheet already exists or not.
        :param worksheet_title: (str) title of the worksheet to check the existence of
        :param spreadsheet_id: (str) name of the spreadsheet to look into (if None, the default spreadsheet of the
            SpreadsheetWrapper instance will be used)
        :return: bool
        """
        sh = self._require_spreadsheet(spreadsheet_id)
        # Get list of worksheet titles and check if it is in it
        worksheet_titles = [worksheet.title for worksheet in sh.worksheets()]
        return worksheet_title in worksheet_titles

    def create_worksheet(self, worksheet_title: str, spreadsheet_id: Optional[str] = None, nb_rows: int = 1000,
                         nb_columns: int = 26, index: Optional[int] = None) -> None:
        """
        Create a new worksheet, identified by its title.
        :param worksheet_title: (str) title of the worksheet to create
        :param spreadsheet_id: (str) name of the spreadsheet to create the worksheet into (if None, the default
            spreadsheet of the SpreadsheetWrapper instance will be used)
        :param nb_rows: (int) number of rows of the empty spreadsheet
        :param nb_columns: (int) number of columns of the empty spreadsheet
        :param index: (int) position of the sheet. If None, the new spreadsheet will be positioned last
        :return: None
        """
        LOGGER.info(f'Creating empty worksheet {worksheet_title}...')
        sh = self._require_spreadsheet(spreadsheet_id)
        sh.add_worksheet(worksheet_title, nb_rows, nb_columns, index)

    def delete_worksheet(self, worksheet_title: str, spreadsheet_id: Optional[str] = None) -> None:
        """
        Delete a worksheet, identified by its title.
        :param worksheet_title: (str) title of the worksheet to delete
        :param spreadsheet_id: (str) name of the spreadsheet the worksheet to delete is in (if None, the default
            spreadsheet of the StorageWrapper instance will be used)
        :return: None
        """
        LOGGER.info(f'Deleting worksheet {worksheet_title}...')
        sh = self._require_spreadsheet(spreadsheet_id)
        worksheet = self._get_worksheet(sh, worksheet_title)
        sh.del_worksheet(worksheet)

    def clear_worksheet(self, worksheet_title: str, spreadsheet_id: Optional[str] = None) -> None:
        """
        Clear all values from a worksheet, identified by its title.
        :param worksheet_title: (str) title of the worksheet to clear
        :param spreadsheet_id: (str) name of the spreadsheet the worksheet to clear is in (if None, the default
            spreadsheet of the StorageWrapper instance will be used)
        :return: None
        """
        LOGGER.info(f'Clearing spreadsheet {worksheet_title}...')
        # Load the worksheet to empty
        sh = self._require_spreadsheet(spreadsheet_id)
        worksheet = self._get_worksheet(sh, worksheet_title)
        # Add an empty column, remove all N columns but this one, and recreate N-1 empty columns
        sh.values_clear("'{worksheet_title}'!A1:{last_colname}{last_rownumber}".format(
            worksheet_title=worksheet_title,
            last_colname=self._get_nth_colname(worksheet.col_count),
            last_rownumber=worksheet.row_count
        ))

    def worksheet_to_df(self, worksheet_title: str, spreadsheet_id: Optional[str] = None) -> pd.DataFrame:
        """
        Read the data from a specific worksheet and return it as a pandas DataFrame.
        :param worksheet_title: (str) title of the worksheet to read
        :param spreadsheet_id: (str) name of the spreadsheet the worksheet to read is in (if None, the default
            spreadsheet of the StorageWrapper instance will be used)
        :return: pandas DataFrame with the worksheet's data
        """
        sh = self._require_spreadsheet(spreadsheet_id)
        # Download data and format it
        data = self._get_worksheet(sh, worksheet_title).get_all_records()
        return pd.DataFrame.from_records(data)

    def df_to_worksheet(self, df: pd.DataFrame, worksheet_title: str, spreadsheet_id: Optional[str] = None,
                        if_exists: str = 'fail', include_index=False, include_header=True) -> None:
        """
        Upload a pandas DataFrame to a specific worksheet, identified by its title.
        :param df: pandas DataFrame to be uploaded to the worksheet
        :param worksheet_title: (str) title of the worksheet to upload the data to
        :param spreadsheet_id: (str) name of the spreadsheet the worksheet to upload the data to is in (if None, the
            default spreadsheet of the StorageWrapper instance will be used)
        :param if_exists: action to take if the worksheet already exists. Should be in ('fail', 'replace')
        :param include_index: (bool) if True, include the DataFrame's index as an additional column. Defaults to False.
        :param include_header: (bool) if True, add a header row or rows before data with column names. Defaults to True.
        :return: None
        """
        # If the worksheet does not exist, create it
        if not self.worksheet_exists(worksheet_title, spreadsheet_id):
            self.create_worksheet(worksheet_title, spreadsheet_id)
        # If it exists, adopt the behavior specified in the "if_exists" argument
        else:
            if if_exists == 'fail':
                raise SheetError(f'Spreadsheet already has a worksheet "{worksheet_title}".'
                                 f'Set "if_exists" to "replace" to clear it before loading data.')
            elif if_exists == 'replace':
                self.clear_worksheet(worksheet_title, spreadsheet_id)
            else:
                raise NotImplementedError('"if_exists" argument must be in ("fail", "replace")')
        # Pre-process data (fill null values)
        sh = self._require_spreadsheet(spreadsheet_id)
        worksheet = self._get_worksheet(sh, worksheet_title)
        set_with_dataframe(worksheet, df, include_index=include_index, include_column_header=include_header)
