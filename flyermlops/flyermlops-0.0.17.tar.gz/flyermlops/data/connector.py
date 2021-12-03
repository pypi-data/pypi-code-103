import awswrangler as wr
from typing import Dict, Any, List, Iterable, Optional, Tuple, Union
import re
import time
import boto3
import psycopg2
from sqlalchemy import create_engine, MetaData, Table
from urllib.parse import quote_plus, urlparse, unquote
import pandas as pd
import io
import teradatasql
import awswrangler as wr

from flyermlops.exceptions import NonActiveModelTrackingID
from .connector_base import ConnectorBase
from . import data_utils as utils


class AthenaHelper(ConnectorBase):
    """Athena helper class for connecting to AWS Athena"""

    def __init__(
        self,
        bucket: str,
        database: str = None,
        boto_sess: str = None,
        region: str = "us-east-1",
        **kwargs,
    ):
        """Instantiates an athena class that extends aws wrangler

        Args:
            bucket: S3 bucket where data will be stored
            boto_sess: Boto session
            database: Athena database
            output_prefix: Where to save temporary athena query data

        """
        super().__init__(
            bucket=bucket,
            boto_sess=boto_sess,
            database=database,
            region=region,
            **kwargs,
        )
        if self._boto_sess is None:
            if self._region is not None:
                self._boto_sess = boto3.Session(region_name=self._region)

        self.athena_client, self.s3_client, self.glue_client = self.set_connection()

    def set_connection(self):
        return (
            self._boto_sess.client("athena"),
            self._boto_sess.resource("s3"),
            self._boto_sess.client("glue"),
        )

    def create_table(
        self,
        query: str,
        table_name: str,
        bucket_prefix: str,
        database: str = None,
        s3_bucket: str = None,
        column_comments: str = None,
        bucketed_columns: List[str] = None,
        bucketed_count: int = None,
        partition_column: List[str] = None,
    ):

        """Creates table from query

        Args:
            query: query. Must be a create statement query
            table_name: Name of table to be created
            bucket_path: S3 prefix where data will be stored
            column_comments: Optional argument to specify column descriptions that will be stored in aws glue

        """

        if self._table_suffix is not None:
            old_table_name = table_name
            table_name = f"{table_name}-{self._table_suffix}"

        query = utils._generate_create_statement(
            query=query,
            database=database or self._database,
            table_name=table_name,
            bucket=s3_bucket or self._bucket,
            bucket_prefix=bucket_prefix,
            bucketed_columns=bucketed_columns,
            bucketed_count=bucketed_count,
            partition_column=partition_column,
        )

        # drop table
        if table_name is not None:
            wr.catalog.delete_table_if_exists(
                database=self._database,
                table=table_name,
                boto3_session=self._boto_sess,
            )

        # delete objects
        _bucket = self.s3_client.Bucket(name=self._bucket)
        if bucket_prefix is not None:
            _bucket.objects.filter(Prefix=f"{bucket_prefix}/").delete()

        # Execute query
        response = self.athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": self._database},
            ResultConfiguration={
                "OutputLocation": f"s3://{self._bucket}/{self._temp_output_prefix}"
            },
        )

        query_execution_id = response["QueryExecutionId"]
        state = utils._wait_for_query_completion(
            self.athena_client, query_execution_id,
        )
        print(f"Query ID {query_execution_id} status: {state}")

        # Update column comments
        if column_comments:
            utils._update_column_coments(
                column_comments=column_comments,
                glue_client=self.glue_client,
                database=self._database,
                table_name=table_name,
            )

        # Delete temp table storage
        _bucket.objects.filter(Prefix=self._temp_output_prefix).delete()

    def read_sql(
        self,
        query: str,
        return_df: bool = True,
        table_name=None,
        bucket_prefix: str = None,
    ):
        """Reads athena SQL query and returns results

        Args:
            query: query
            return_df: Whether to return a dataframe from the query
            table_name: Name of table (if writing a create statement)

        Returns:
            Pandas dataframe

        """
        if return_df:
            df = wr.athena.read_sql_query(
                query,
                database=self._database,
                s3_output=f"s3://{self._bucket}/{self._temp_output_prefix}",
                keep_files=False,
                max_cache_seconds=0,
                boto3_session=self._boto_sess,
            )

            # delete temp objects
            _bucket = self.s3_client.Bucket(name=self._bucket)
            _bucket.objects.filter(Prefix=self._temp_output_prefix).delete()

            return df

        else:
            self.create_table(
                query=query, table_name=table_name, bucket_prefix=bucket_prefix,
            )

    def df_to_athena(
        self,
        data: pd.DataFrame,
        bucket_prefix: str,
        table_name: str,
        partition_cols: List[str] = None,
        columns_comments: Dict[str, str] = None,
        mode: str = "append",
        bucketing_info: Optional[Tuple[List[str], int]] = None,
    ):

        """Saves pandas dataframe as athena table

        Args:
            data: Pandas dataframe.
            bucket_path: Where data will be stored in S3.
            table_name: Name of table.
            parition_cols: List of columns to create partitions on.
            columns_comments: Argument to specify column descriptions that will be stored in aws glue.
            mode: ``append`` (Default), ``overwrite``, ``overwrite_partitions``.

        """

        # Write to Athena
        wr.s3.to_parquet(
            df=data,
            path=f"s3://{self._bucket}/{bucket_prefix}/",  # where data will be stored in S3
            dataset=True,  # enables partitioning and table creation
            database=self._database,  # database to use; database must already exist
            table=table_name,
            partition_cols=partition_cols,
            bucketing_info=bucketing_info,
            mode=mode,  # overwrite (default is append)
            compression="snappy",
            concurrent_partitioning=True,  # compression saves cost for S3 and Athena
            use_threads=True,  # enable concurrent requests
            sanitize_columns=True,
            boto3_session=self._boto_sess,  # specify boto3 session with region
            columns_comments=columns_comments,
        )

        print(f"Created {self._database}.{table_name} in Athena")

    def df_to_s3(
        self,
        data: pd.DataFrame,
        bucket_prefix: str,
        partition_cols: List[str] = None,
        bucketing_info: Optional[Tuple[List[str], int]] = None,
    ):
        wr.s3.to_parquet(
            df=data,
            path=f"s3://{self._bucket}/{bucket_prefix}",  # where data will be stored in S3
            partition_cols=partition_cols,
            bucketing_info=bucketing_info,
            boto3_session=self._boto_sess,
        )

    def read_parquet(
        self, path: Union[str, List[str]], columns: Optional[List[str]] = None,
    ):
        df = wr.s3.read_parquet(
            path=path, columns=columns, boto3_session=self._boto_sess,
        )

        return df

    def get_table_schema(self, table: str):
        table_schema = wr.catalog.get_table_types(
            database=self._database, table=table, boto3_session=self._boto_sess,
        )
        return table_schema


class PostgresHelper(ConnectorBase):
    """Postgres helper class for connecting to postgres databases."""

    def __init__(
        self,
        host: str = None,
        user: str = None,
        password: str = None,
        port: int = None,
        database: str = None,
        uri: str = None,
    ):

        super().__init__(
            host=host,
            user=user,
            password=password,
            port=port,
            database=database,
            uri=uri,
        )

        if self._uri is not None:
            self._parse_uri()

    def _parse_uri(self):

        parsed = urlparse(self._uri)
        self._user = unquote(parsed.username)
        self._password = unquote(parsed.password)
        self._host = unquote(parsed.hostname)
        self._port = parsed.port
        self._database = unquote(parsed.path[1:])

    def set_connection(self, connector: str):
        """Creates sql engine for Postgres Aurora. Supports psycopg2 and sqlalchemy

        Args:
            connector: Type of engine to create (either "psycopg2" or "sqlalchemy")

        Returns:
            sqlalchemy.engine.Engine or psycopg2.extensions.connection
        """

        if connector == "psycopg2":
            try:
                return psycopg2.connect(
                    host=self._host,
                    user=self._user,
                    password=self._password,
                    port=self._port,
                    database=self._database,
                )
            except Exception as e:
                raise e

        elif connector == "sqlalchemy":
            try:
                return create_engine(
                    f"postgresql+psycopg2://"
                    f"{quote_plus(self._user)}:{quote_plus(self._password)}@{self._host}:{self._port}/{self._database}"
                )
            except Exception as e:
                raise e

    def read_sql(self, query, return_df=False):
        """
        Executes query

        Args:
            query: Query string
        """
        con = self.set_connection(connector="psycopg2")
        con.autocommit = True
        try:
            with con.cursor() as cur:
                print(f"Executing query")
                cur.execute(query)
                if return_df:
                    data = cur.fetchall()
                    col_names = [desc[0] for desc in cur.description]
                    return pd.DataFrame(data, columns=col_names)
                else:
                    print("Query status: complete")
        except Exception as e:
            raise e

    def df_to_postgres(
        self,
        df,
        table_name,
        schema_name,
        mode="fail",
        sep_val="\t",
        null_val="",
        verbose=False,
    ):
        """
        Efficiently load data into Postgres from pandas DataFrame.

        Args:
            df : pandas.DataFrame
                Query can be any valid PostgreSQL statement.
            table_name : str
                Target table name in Aurora.
            schema_name: str
                Target schema name in Aurora.
            mode: {'fail', 'replace', 'append'}, optional [default is "fail"]
                Write mode to use, if table already exists.
            sep_val: str, optional [default is "\t"]
                Sets separator value.
            null_val: str, optional [default is ""]
                Sets default value for nulls.
            verbose: bool, optional
                Prints completion message, if set to True.

        Returns:
            pandas.DataFrame
        """
        engine = self.set_connection(connector="sqlalchemy")
        # raw_connection overcomes limitations imposed by DB API connection
        raw_con = engine.raw_connection()
        cur = raw_con.cursor()
        csv_like_stringio_object = io.StringIO()
        try:
            df.to_csv(
                path_or_buf=csv_like_stringio_object,
                sep=sep_val,
                header=False,
                index=False,
            )  # convert data to StringIO object
            csv_like_stringio_object.seek(0)  # set StringIO cursor
            df.head(0).to_sql(
                name=table_name,
                schema=schema_name,
                con=engine,
                if_exists=mode,
                index=False,
            )  # create table in Aurora
            cur.execute("SET search_path TO " + schema_name)  # set Aurora schema
            cur.copy_from(
                file=csv_like_stringio_object,
                table=table_name,
                sep=sep_val,
                null=null_val,
            )
            raw_con.commit()
            if verbose:
                print(f"Data successfully loaded into {schema_name}.{table_name}.")
        except Exception as e:
            print(e)
        finally:
            csv_like_stringio_object.close()
            cur.close()
            raw_con.close()
            engine.dispose()


class TeradataHelper(ConnectorBase):
    """Helper class for connecting to Teradata."""

    def __init__(
        self, user: str, password: str, host: str, logmech: str, port: int = None,
    ):
        super().__init__(
            host=host, user=user, password=password, port=port, logmech=logmech,
        )

    def set_connection(self):
        self._port = [self._port or None][0]

        params = {
            "user": self._user,
            "password": self._password,
            "host": self._host,
            "logmech": self._logmech,
        }
        if self._port is not None:
            self._port = int(self._port)
            params["dbs_port"] = self._port

        try:
            conn = teradatasql.connect(**params)
            print("Connected to terradata")
            return conn

        except Exception as e:
            raise e

    def read_sql(self, query):

        """Execute sql statement

        Args:
            query: Query statement

        Returns:
            pandas.DataFrame
        """

        conn = self.set_connection()
        df = pd.read_sql(query, conn)
        return df


class DataConnector:
    """Helper class for connecting to different data clients."""

    def __init__(self, style):
        self.style = style
        self.client = self._get_client()

    def _get_client(self):
        return {
            "athena": AthenaHelper,
            "postgres": PostgresHelper,
            "teradata": TeradataHelper,
        }.get(self.style)

