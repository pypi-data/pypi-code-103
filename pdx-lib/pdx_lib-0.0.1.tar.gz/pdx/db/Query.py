from pdx import Console
from pdx.db import OracleConnection
import cx_Oracle

out = Console.get()


class Query:
    query = None
    parameter_list = None
    cx = None
    rows_affected = None
    cursor = None

    def value(self):
        """Get a single value from a given query"""
        out.trace("Query.value()")
        try:
            return self.list(1)[0][0]
        except IndexError:
            return None

    def list_values(self, max_results=None):
        """
        Run a single-column SELECT query and return results as a list of data
        :return: List of data
        """
        out.trace("Query.list_values()")
        data = []
        for rr in self.list(max_results):
            data.append(rr[0])

        return data

    def list(self, max_results=None):
        """
        Run a SELECT query and return results as a list of lists
        :return: List of lists
        """
        out.trace("Query.list()")

        # Run the query
        self.run()

        # If returning all rows
        if max_results is None:
            results = self.cursor.fetchall()

        # If returning limited number of results
        else:
            results = []
            for ii in range(0, max_results):
                # Get the next result
                row = self.cursor.fetchone()

                # Exit when no more results
                if row is None:
                    break

                # Add row to results
                results.append(row)

        # Close the cursor (Connection is still open)
        self.cursor.close()

        return results

    def map(self, max_results=None):
        """
        Run a two-column SELECT query and return results as a map:
            map[column1] = column2

        :return: Map (dict)
        """
        out.trace("Query.map()")

        results = {}

        # Run the query and put into a map
        try:
            for row in self.list(max_results):
                results[row[0]] = row[1]

            return results
        except IndexError:
            out.put_error("Query.map() expects a two-column select query")
            return None

    def results(self):
        """
        Run a SELECT query and return results as a list of maps
        :return: List of dicts with column names as keys
        """
        out.trace("Query.results()")

        # Run the query
        self.run()

        # Generate a list of dicts from the cursor
        # https://stackoverflow.com/questions/10455863/making-a-dictionary-list-with-cx-oracle
        columns = [ii[0] for ii in self.cursor.description]
        result = [dict(zip(columns, row)) for row in self.cursor]
        del columns

        # Close the cursor
        self.cursor.close()

        return result

    def execute(self):
        """
        Execute an INSERT/UPDATE/DELETE query.
        Returns: The number of rows affected

        Note: THIS CLOSES THE CURSOR
        """
        out.trace("Query.execute")
        self.num_rows_affected = None
        try:
            # Run the query
            self.run(True)

            # Close the cursor
            self.cursor.close()

        except Exception as ee:
            out.unexpected_error(ee, "Error executing query")

        return self.num_rows_affected

    def run(self, commit_transaction=False):
        """
        Execute any query and obtain the cursor.

        Note: LEAVES CURSOR OPEN
        """
        out.trace("Query.run")
        out.log_debug(self.query)
        try:

            # If connected, run query
            if self.cx:
                self.cursor = cx_Oracle.Cursor(self.cx)
                if self.parameter_list is None:
                    self.cursor.execute(self.query)
                else:
                    self.cursor.prepare(self.query)
                    self.cursor.execute(None, self.parameter_list)

                self.num_rows_affected = self.cursor.rowcount
                out.log_debug("Rows affected: {0}".format(self.num_rows_affected))

                # Commit the query, if specified in parameters
                if commit_transaction:
                    self.commit()

                # Connection cannot be closed here, or the cursor will be unusable
                # Calling function should handle the connection

                return self.num_rows_affected

            else:
                out.put_error("No connection was passed to Query.run()")
                return None

        except Exception as ee:
            out.unexpected_error(ee, "Error getting cursor from query")
            return None

        out.put_error("No value returned from Query.run()")
        return None

    def commit(self):
        out.trace('Query.commit')
        self.cx.commit()

    def __init__(self, cx, query, parameter_list=None):
        """Run a basic query"""

        # Allow the connection to be specified in multiple ways

        # cx_Oracle connection
        if cx and type(cx) is cx_Oracle.Connection:
            out.log_debug("Query connection from existing cx_Oracle.Connection")
            self.cx = cx
        # pdx.db.OracleConnection
        elif cx and 'OracleConnection' in str(type(cx)):
            out.log_debug("Query connection from existing pdx.db.OracleConnection")
            self.cx = cx.cx
        # SID string (creates connection as Session.username)
        elif cx and type(cx) is str and len(cx) == 4:
            out.log_debug("Query connection from an SID")
            self.cx = OracleConnection.OracleConnection(cx).cx
        else:
            out.put_error("Cannot run query on connection of type {0}".format(type(cx)))

        # Query must be a string
        if type(query) is str:
            # Query should not include the ";"
            self.query = query.strip('"; ')

        # Parameters (if any) must be in a list
        if type(parameter_list) is list:
            self.parameter_list = parameter_list
        elif parameter_list:
            out.put_error("Query parameters must be in a list")

        self.cursor = None
        self.num_rows_affected = None
