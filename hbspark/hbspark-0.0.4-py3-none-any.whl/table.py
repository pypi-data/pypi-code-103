# _table.py
# Internal table methods
# Kris Zhao

"""
Holds all tabling functionality for hbspark, including creating, deletion, querying, and modifications.
"""

###################
#     Imports     #
###################
# Get global session which holds setup information
from . import _hb_session as hb_session

# Grab all utility functions
from ._utils import *

###################
#     Methods     #
###################
# List out existing tables
# Returns list of strings of table names
def tables():
    """
    Get all of the tables at the initialized HBase connection.

    @rtype: C{list} of C{string}
    @return: A list of the string names of the tables stored at the HBase connection L{hbspark._hb_session.conn}
    """
    return binlist_to_strlist(hb_session.query("tables"))

# Select a specific table based on string name
# Returns reference to a selected table as a _table.Table object
def table(table_name):
    """
    Get an instance of a specific table that can have queries performed on it.

    @type table_name: string
    @param table_name: The name for the table to be returned.

    @rtype: L{hbspark.table.Table}
    @return: The table instance, permitting various querying and modification operations.
    """
    if(hb_session.isInitialized()):
        return Table(table_name)
    return None

# Check if table name exists
# Return boolean of existence
def has_table(table_name):
    """
    Determine if the HBase connection contains the specified tablename.

    @type table_name: string
    @param table_name: The name for the table to be checked.

    @rtype: bool
    @return: True if the connection contains C{table_name}, false otherwise.
    """
    return table_name in tables()

# Create a new table in HBase
# Returns the _table.Table reference holder.
def create_table(name, families):
    #TODO Verify lists for family paremeters:
    """
    Create a new table inside HBase.

    @type name: string
    @param name: The new table's name.

    @type families: C{dict : (string -> dict: (attr -> val))}
    @param families: C{dict} of column family names to the column U{settings<blank>}.

    @rtype: L{hbspark.table.Table}
    @return: An instance of the newly created table 
    """
    # First create the new table
    hb_session._create_table(name, families)
    return Table(name) #Then select it by creating the object

# Delete a table:
# Returns None, deletes the corresponding table.
def delete_table(name, disabled=False):
    """
    Deletes an existing table from the HBase connection.

    @type name: string
    @param name: The name of the table that is to be deleted.

    @type disabled: bool
    @param disabled: Whether or not tables should only be deleted if they are disabled in hbase (False), or if any table regardless of status can be deleted (True) .

    @rtype: None
    @return: No return
    """
    hb_session._delete_table(name, disabled)

# Get a table (or create an empty one)
# Returns _table.Table object
def get_or_create_table(table_name, families):
    """
    Gets the table provided by C{table_name} or creates a new one with the provided column families from C{families}.

    @type table_name: string
    @param table_name: The name of the HBase table.

    @type families: C{dict : (string -> dict: (attr -> val))}
    @param families: C{dict} of column family names to the column U{settings<blank>}.

    @rtype: L{hbspark.table.Table}
    @return: An instance of the provided C{table_name} either newly created or not. 
    """

    if(has_table(table_name)):
        return table(table_name)
    else:
        return create_table(table_name, families)

# Get the column families inside a table:
# Returns Dict for each column family.
def families(table_name):
    """
    Get all of the families for a specific HBase table.

    @type table_name: string
    @param table_name: The name of the HBase table.

    @rtype: C{dict : (string -> dict: (attr -> val))}
    @return: C{dict} of column family names to the column family's HBase attributes.
    """

    ret_table = table(table_name)
    return ret_table.families() if ret_table is not None else ret_table

###################
#     Objects     #
###################
class Table:
    """
    Represents the instance of the HBase table.
    """

    def __init__(self, name):
        """
        Instantiates a new table object with a given table name.

        @type name: string
        @param name: The name for the table to be created.

        @rtype: L{hbspark.table.Table}
        @return: A new instance of the HBase table.
        """
        self._table_ref = hb_session.query("table", name)

    # Informational:
    def families(self):
        """
        Gets all of the column families associated with the HBase tables.

        @rtype: list
        @return: A list of dictionaries representing each column family in the table and it's configuration.
        """

        return bindict_to_strdict(self._table_ref.families())

    def regions(self):
        """
        Provides all of the regions associated with a table (between the keys).

        @rtype: list
        @return: A list of dictionaries representing a region and it's configuration.
        """

        return bindict_to_strdict(self._table_ref.regions())

    # Specific data retrieval
    def row(self, rowkey, columns=None, timestamp=None, include_timestamp=False):
        """
        Get a row from the HBase.

        @type rowkey: string
        @param rowkey: The rowkey for the provided row.

        @type columns: C{list} of C{string}
        @param columns: The column names which should be retrieved from the row.

        @type timestamp: int
        @param timestamp: The new timestamp for the retreival. (VF)

        @type include_timestamp: bool
        @param include_timestamp: Whether or not to include the timestamp in the retreival. (VF)

        @rtype: U{pyspark.sql.Row<https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.sql.Row.html>}
        @return: The row as a spark manageable data structure.
        """
        return hb_session.create_row(**bindict_to_strdict(self._table_ref.row(str(rowkey), columns=columns, timestamp=timestamp, include_timestamp=include_timestamp)))

    #TODO Convert to pyspark
    def cell(self, rowkey, column, versions=None, timestamp=None, include_timestamp=False):
        """
        Retrieve the cell value (and it's hisotry) from the HBase table.

        @type rowkey: string
        @param rowkey: The rowkey for the target cell.

        @type column: string
        @param column: The column name for the target cell.
        
        @type versions: int
        @param versions: The maximum numbers of cell versions to be retrieved.
        
        @type timestamp: int
        @param timestamp: The new timestamp for the retreival. (VF)

        @type include_timestamp: bool
        @param include_timestamp: Whether or not to include the timestamp in the retreival. (VF)

        @rtype: C{list} of U{pyspark.sql.Row <https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.sql.Row.html>}
        @return: List of each retrieved row from the table.
        """

        return self._table_ref.cells(rowkey, column, versions=versions, timestamp=timestamp, include_timestamp=include_timestamp)

    # Table modification:
    def put(self, rowkey, data, timestamp=None, wal=True):
        """
        Insert a new row into the HBase table.

        The C{data} payload should have the following structure::

            data = {
                "cf_x:col_x" : "value",
                ...
            }
        
        @type rowkey: string
        @param rowkey: The rowkey for the new inserted row.
        
        @type data: dict
        @param data: The dictionary mapping C{cf:col} to values to be stored.

        @type timestamp: int
        @param timestamp: The timestamp used for the put operation (VF).

        @type wal: bool
        @param wal: Whether or not to write to the WAL of HBase.

        @rtype: None
        @return: Method does not return.

        """

        dataDict = data.asDict(True) #Must be structured as "columnfamily:column"
        # print(dataDict)
        return self._table_ref.put(rowkey, dataDict, timestamp=None, wal=True)

    def put_dict(self, rowkey, data, timestamp=None, wal=True):
        """
        Insert a new row into the HBase table.

        The C{data} payload should have the following structure::

            data = {
                "cf_x:col_x" : "value",
                ...
            }
        
        @type rowkey: string
        @param rowkey: The rowkey for the new inserted row.
        
        @type data: dict
        @param data: The dictionary mapping C{cf:col} to values to be stored.

        @type timestamp: int
        @param timestamp: The timestamp used for the put operation (VF).

        @type wal: bool
        @param wal: Whether or not to write to the WAL of HBase.

        @rtype: None
        @return: Method does not return.

        """
        # print(dataDict)
        return self._table_ref.put(rowkey, data, timestamp=None, wal=True)

    # Deletes the row at the given rowkey, can specify columns.
    def delete(self, rowkey, columns=None, timestamp=None, wal=True):
        """
        Delete a row from the HBase table.

        The C{columns} payload should have the following structure::

            columns = ["cf_x:col_x", ...]

        @type rowkey: string
        @param rowkey: The rowkey targeting the row to be deleted.

        @type columns: list
        @param columns: The list of column names to be deleted of the form C{cf:col}.

        @type timestamp: int
        @param timestamp: The timestamp for the deletion operation.

        @type wal: bool
        @param wal: Whether or not to insert into the WAL for HBase

        @rtype: None
        @return: Method does not return.
        """

        return self._table_ref.delete(rowkey, columns=columns, timestamp=timestamp, wal=wal)

    #For bulk puts / deletes of rows.
    def batch(self, timestamp=None, batch_size=None, transaction=False, wal=True):
        """
        Retrieve the batch processor of the table which allows for bulk data modification.

        @type timestamp: int
        @param timestamp: The timestame all batch commands should utilize.

        @type batch_size: int
        @param batch_size: The queue length for the batch process before commands should C{send} automatically.

        @type transaction: bool
        @param transaction: Whether or not the batch should behave like a transaction (for the purposes of a context manager).

        @type wal: bool
        @param wal: Whether to write to the WAL

        @rtype: L{hbspark.table.Table.Batch}
        @return: The batch processor for the current table. 
        """

        return self.Batch(self._table_ref.batch(timestamp=timestamp, batch_size=batch_size, transaction=transaction, wal=wal))

    # *COUNTERS?*

    # Creates a new dataframe from the specified scan
    # Appends rowkey to the front of the dictionary
    def scan(
        self,
        schema=None,
        row_start=None, 
        row_stop=None, 
        row_prefix=None, 
        columns=None, 
        filter=None, 
        timestamp=None, 
        include_timestamp=False, 
        batch_size=1000, 
        scan_batching=None, 
        limit=None, 
        sorted_columns=False, 
        reverse=False
    ):
        """
        Retrieve all of the rows inside the HBase table.

        @type schema: StructType
        @param schema: A list of StructField with ("cf:name", Type(), True)

        @type row_start: string
        @param row_start: Beginning rowkey of the scan (inclusive).


        @type row_stop: string
        @param row_stop: Ending rowkey of the scan (exclusive)

        @type row_prefix: string
        @param row_prefix: A prefix rowkeys must match.

        @type columns: list or tuple
        @param columns: The columns that should be returned for each row.

        @type filter: string
        @param filter: A string to filter out results (VF)

        @type timestamp: int 
        @param timestamp: The timestamp for the scan.

        @type include_timestamp: int
        @param include_timestamp: Whether row timestamps are returned.

        @type batch_size: int
        @param batch_size: The max size for a single return of retrieving results.

        @type scan_batching: bool
        @param scan_batching:Whether or not the server will return by batching.

        @type limit: int
        @param limit: Maximum number of total returned rows

        @type sorted_columns: bool
        @param sorted_columns: Whether to return the sorted columns or not.

        @type reverse: bool
        @param reverse: Whether to perform scans in reverse of natural order.
        
        @rtype: U{pyspark.sql.DataFrame<https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.sql.DataFrame.html#pyspark.sql.DataFrame>}
        @return: A dataframe that consists of all the rows in the HBase table.
        """
        data_generator = self._table_ref.scan(
            row_start=row_start, 
            row_stop=row_stop, 
            row_prefix=row_prefix, 
            columns=columns, 
            filter=filter, 
            timestamp=timestamp, 
            include_timestamp=include_timestamp, 
            batch_size=batch_size, 
            scan_batching=scan_batching, 
            limit=limit, 
            sorted_columns=sorted_columns, 
            reverse=reverse
        )

        return hb_session.create_data_frame([
            dict(bindict_to_strdict(column_data),rowkey=row_index.decode("utf-8")) for row_index, column_data in data_generator
        ], schema)

    class Batch:
        """
        The batch interface provided for a L{hbspark.table.Table}.
        """
        def __init__(self, hb_batch):
            """
            Creates a new batch processor for a L{hbspark.table.Table} instance.

            Should B{only} be initialized through L{hbspark.table.Table.batch} and not called by the user separately.

            @type hb_batch: U{happybase.Batch<https://happybase.readthedocs.io/en/latest/api.html#happybase.Batch>}
            @param hb_batch: The C{happybase} batch link that allows batch operations on the current table.

            
            @rtype: L{hbspark.table.Table.Batch}
            @return: A new instance of the batch processor.
            """

            self._hb_batch = hb_batch
            """
            The corresponding Happybase batch processesor.
            """

        # Submit the batch process
        def send(self):
            """
            Send all of the pending changes loaded into the batch process.

            @rtype: None
            @return: Method does not return.
            """
            self._hb_batch.send()

        # Put the Pyspark row into the database
        def put(self, rowkey, data, wal=None):
            """
            Load a new put operation into the batch.
            
            The C{data} payload should have the following structure::

                data = {
                    "cf_x:col_x" : "value",
                    ...
                }
            
            @type rowkey: string
            @param rowkey: The rowkey for the new inserted row.
            
            @type data: dict
            @param data: The dictionary mapping C{cf:col} to values to be stored.

            @type wal: bool
            @param wal: Whether or not to write to the WAL of HBase.

            @rtype: None
            @return: Method does not return.

            """
            self._hb_batch.put(rowkey, data.asDict(True), wal=wal)

        def put_dict(self, rowkey, data, wal=None):
            """
            Load a new put operation into the batch.
            
            The C{data} payload should have the following structure::

                data = {
                    "cf_x:col_x" : "value",
                    ...
                }
            
            @type rowkey: string
            @param rowkey: The rowkey for the new inserted row.
            
            @type data: dict
            @param data: The dictionary mapping C{cf:col} to values to be stored.

            @type wal: bool
            @param wal: Whether or not to write to the WAL of HBase.

            @rtype: None
            @return: Method does not return.

            """
            self._hb_batch.put(rowkey, data, wal=wal)

        def delete(self, rowkey, column=None, wal=None):
            """
            Load a new delete operation into the batch.

            The C{column} payload should have the following structure::

                column = ["cf_x:col_x", ...]

            @type rowkey: string
            @param rowkey: The rowkey targeting the row to be deleted.

            @type column: list
            @param column: The list of column names to be deleted.

            @type wal: bool
            @param wal: Whether or not to insert into the WAL for HBase.
            
            @rtype: None
            @return: Method does not return.
            """
            self._hb_batch.put(rowkey, column=column, wal=wal)

