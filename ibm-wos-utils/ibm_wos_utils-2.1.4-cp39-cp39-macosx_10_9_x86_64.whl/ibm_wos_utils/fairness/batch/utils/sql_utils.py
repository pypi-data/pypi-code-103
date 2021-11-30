# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2020
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


class SQLUtils():

    @classmethod
    def get_cat_filter_query(cls, col_name: str, operator: str, values: list) -> str:
        query = ""
        for val in values:
            query += "{} {} '{}' or ".format(col_name, operator, val)
        # Removing the last `or` and white spaces
        query = query[0:len(query) - 4]
        return query

    @classmethod
    def get_num_filter_query(cls, col_name: str, ranges: list) -> str:
        query = ""
        for range_list in ranges:
            query += "({} {} {} and {} {} {}) or ".format(col_name,
                                                          ">=", range_list[0], col_name, "<=", range_list[1])
        # Removing the last `or` and white spaces
        query = query[0:len(query) - 4]
        return query

    @classmethod
    def concat_query(cls, query1: str, operator: str, query2: str) -> str:
        query = ""
        query1 = "({})".format(query1)
        query2 = "({})".format(query2)
        query = "{} {} {}".format(query1, operator, query2)
        return query
