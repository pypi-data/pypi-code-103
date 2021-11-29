import logging
import warnings
from abc import abstractmethod
from typing import Optional, Union, Sequence, List, Dict, Tuple

from dslib.utils import timeit

try:
    import pandas as pd
    import psycopg2
    import pymysql
    from pandas.io.sql import pandasSQL_builder, _wrap_result
    from sqlalchemy import create_engine
    from sqlalchemy.exc import SQLAlchemyError
except ImportError as e:
    raise ImportError('Please install "database" extra packages.') from e

# Set up logger
LOGGER = logging.getLogger(__name__)
warnings.filterwarnings('ignore', message=r'\(1003\,')  # Hide pymysql 1003 persistent warning


class _DatabaseWrapper(object):

    def __init__(self, conn, expected_db_type):
        if not conn.__class__.__name__ == 'Engine':
            raise ValueError('"conn" argument must be a SQLAlchemy "Engine" instance')
        if not expected_db_type == conn.name:
            ValueError(f'Provided connector should be "{expected_db_type}" (current: "{conn.name}")')
        self.conn = conn
        self.db_type = conn.name
        self._pandas_sql = pandasSQL_builder(self.conn)

    @classmethod
    @abstractmethod
    def from_params(cls, *args, **kwargs):
        raise NotImplementedError

    def _execute(self, query, *args, **kwargs):
        return self._pandas_sql.execute(query, *args, **kwargs)

    def assess_query(self, query: str) -> bool:
        """
        Assesses whether the query is valid or not.
        :param query: query to be executed
        :return: bool
        """
        try:
            self._execute(f'EXPLAIN {query}', output_type=None)
        except SQLAlchemyError as e:
            LOGGER.error(f'Query is not valid: \n{str(e)}')
            return False
        else:
            LOGGER.info(f'Query is valid')
            return True

    def run_query(self, query: str, output_type: Optional[str] = 'df', index_col: Union[str, List[str], None] = None,
                  coerce_float: bool = True, parse_dates: Union[List[str], Dict[str, str], None] = None
                  ) -> Union[pd.DataFrame, None]:
        """
        Runs a query and returns the output in the specified format
        :param query: query to be executed
        :param output_type: output type of the run_query function. One of ['df', None]. Defaults to 'df'
        :param index_col: column(s) to set as index(MultiIndex)
        :param coerce_float: attempts to convert values of non-string, non-numeric objects (like decimal.Decimal) to
            floating point. Can result in loss of Precision
        :param parse_dates: either a list of column names to parse as dates, a dict of ``{column_name: format string}``,
            or a dict of ``{column_name: arg dict}``, where the arg dict corresponds to the keyword arguments of
            `pandas.to_datetime` function
        :return: results in the chosen output_type
        """
        # Execute query
        with timeit(text='Executing query took:', logger=LOGGER):
            result = self._execute(query)
        # Return if output_type is None
        if output_type is None:
            return
        # Else return the result as a Pandas DF
        elif output_type == 'df':
            with timeit(text='Fetching df took:', logger=LOGGER):
                columns = result.keys()
                data = result.fetchall()
                f = _wrap_result(data, columns, index_col=index_col, coerce_float=coerce_float, parse_dates=parse_dates)
                return f
        else:
            raise NotImplementedError('Argument output_type must be in: ["df", None]')

    @staticmethod
    def _parse_table_reference(table_reference: str) -> Tuple:
        table_name_split = table_reference.split('.')
        if len(table_name_split) == 1:
            return None, table_reference
        elif len(table_name_split) == 2:
            return tuple(table_name_split)
        else:
            raise ValueError('Table reference must be in format: "table_name" or "schema_name.table_name"')

    def exists(self, table_name: str, schema: str = None) -> bool:
        """"
        Check whether a table already exists or not.
        :param table_name: name of the table to check the existence of
        :param schema: name of the schema of the table to check the existence of
        :return: bool
        """
        return self.conn.dialect.has_table(self.conn, table_name, schema=schema)

    @timeit(text='Uploading df to table took:', logger=LOGGER)
    def to_table_from_df(self, df: pd.DataFrame, table_reference: str, if_exists: str = 'fail', index: bool = False,
                         index_label: Union[str, Sequence, None] = None) -> None:
        """
        Uploads a DataFrame to a table and creates it if it does not exist yet.
        :param df: pandas DataFrame to upload to BigQuery
        :param table_reference: reference of the table to create/append/replace (e.g. "warehouse.trip_fill" or
            "bbc-data-platform.warehouse.trip_fill")
        :param if_exists: action to take if the table already exists. Should be in ('fail', 'append', 'replace')
        :param index: write df index as a column. Uses `index_label` as the column name in the table
        :param index_label: column label for index column(s). If None is given (default) and `index` is True, then the
            index names are used.
        :return: None
        """
        schema, table = self._parse_table_reference(table_reference)
        df.to_sql(table, con=self.conn, schema=schema, if_exists=if_exists, index=index, index_label=index_label)

    @timeit(text='Running query and storing results into table took:', logger=LOGGER)
    def to_table_from_query(self, query: str, table_reference: str, if_exists: str = 'fail') -> None:
        """
        Run a query and load its result into a table.
        :param query: query to be executed
        :param table_reference: reference of the table to create/append/replace (e.g. "table_name" or
            "schema_name.table_name")
        :param if_exists: behaviour to adopt when uploading results to BigQuery. Ignored when `to_table` is not
            provided. If provided, must be in ('fail', 'append', 'replace'). Defaults to 'fail'
        :return: None
        """
        schema, table = self._parse_table_reference(table_reference)
        if not self.exists(table, schema):
            self._execute(f'CREATE TABLE {table_reference} AS {query}')
        else:
            if if_exists == 'fail':
                raise ValueError(f'"{table_reference}" table already exists and if_exists set to {if_exists}')
            elif if_exists == 'replace':
                truncate_statement = 'DELETE FROM' if self.db_type == 'sqlite' else 'TRUNCATE TABLE'
                self._execute(f'{truncate_statement} {table_reference};')
                self._execute(f'INSERT INTO {table_reference} {query};')
            elif if_exists == 'append':
                self._execute(f'INSERT INTO {table_reference} {query};')
            else:
                raise NotImplementedError('"if_exists" argument must be in ("fail", "replace", "append")')


class PostgresWrapper(_DatabaseWrapper):

    def __init__(self, conn):
        super(PostgresWrapper, self).__init__(conn, 'postgres')

    @classmethod
    def from_params(cls, host: str, port: int, db_name: str, user: str, password: str, **_) -> _DatabaseWrapper:
        return _DatabaseWrapper(create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}'),
                                'postgres')


class MysqlWrapper(_DatabaseWrapper):

    def __init__(self, conn):
        super(MysqlWrapper, self).__init__(conn, 'mysql')

    @classmethod
    def from_params(cls, host: str, port: int, db_name: str, user: str, password: str, **_) -> _DatabaseWrapper:
        return _DatabaseWrapper(create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}'), 'mysql')


class SqliteWrapper(_DatabaseWrapper):

    def __init__(self, conn):
        super(SqliteWrapper, self).__init__(conn, 'sqlite')

    @classmethod
    def from_params(cls, db_filepath: str, **_) -> _DatabaseWrapper:
        return _DatabaseWrapper(create_engine(f'sqlite:///{db_filepath}'), 'sqlite')
