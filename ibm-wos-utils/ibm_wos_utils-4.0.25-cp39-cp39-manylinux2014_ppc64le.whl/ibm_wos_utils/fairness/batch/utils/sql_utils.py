# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


class SQLUtils():

    @classmethod
    def get_cat_filter_query(cls, col_name: str, operator: str, values: list, concat_operator: str="or") -> str:
        """
        Returns the query for categorical columns for the given column in the given values using the given operator.
        :col_name: The column name.
        :operator: The operator.
        :values: The values to be included in the query.
        :concat_operator: The operator to be used for concatenation of multiple filters.

        :returns: The query.
        """
        query = ""
        for val in values:
            query += "`{}` {} '{}' {} ".format(col_name, operator, val, concat_operator)
        # Removing the last concat operator and white spaces
        query = query[0:len(query) - 2 - len(concat_operator)]
        return query

    @classmethod
    def get_num_filter_query(cls, col_name: str, ranges: list, include:bool=True, concat_operator: str="or") -> str:
        """
        Returns the query which includes/excludes(based on flag `include`) the rows with the given group.
        :col_name: The column name.
        :ranges: The ranges to be used.
        :include: Whether the rows should include/exclude the rows.
        :concat_operator: The operator to be used for concatenation of multiple filters.

        :returns: The query.
        """
        query = ""
        for range_list in ranges:
            if include:
                query += "(`{}` {} {} and `{}` {} {}) {} ".format(col_name,
                                                            ">=", range_list[0], col_name, "<=", range_list[1], concat_operator)
            else:
                query += "(`{}` {} {} or `{}` {} {}) {} ".format(col_name,
                                                            "<", range_list[0], col_name, ">", range_list[1], concat_operator)
        # Removing the last concat operator and white spaces
        query = query[0:len(query) - 2 - len(concat_operator)]
        return query

    @classmethod
    def concat_query(cls, query1: str, operator: str, query2: str) -> str:
        """
        Concatenates the given queries using the given opeartor.
        :query1: The first query to be concatenated.
        :operator: The operator to be used for concatenation.
        :query 2: The second query to be concatenated.

        :returns: The concatenated query.
        """
        query = ""
        query1 = "({})".format(query1)
        query2 = "({})".format(query2)
        query = "{} {} {}".format(query1, operator, query2)
        return query
