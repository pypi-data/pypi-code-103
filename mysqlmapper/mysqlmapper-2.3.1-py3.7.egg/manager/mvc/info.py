from typing import Dict

# noinspection SpellCheckingInspection
_table_xml = """
<xml>
    <mapper column="TABLE_NAME" parameter="Name"/>
    <mapper column="ENGINE" parameter="Engine"/>
    <mapper column="TABLE_COLLATION" parameter="Collation"/>
    <mapper column="TABLE_COMMENT" parameter="Comment"/>
    <mapper column="IFNULL(AUTO_INCREMENT, -1)" parameter="AutoIncrement"/>
    <sql>
        <key>GetList</key>
        <value>
            SELECT
                TABLE_NAME, ENGINE, TABLE_COLLATION, TABLE_COMMENT, IFNULL(AUTO_INCREMENT, -1)
            FROM
                information_schema.TABLES
            WHERE
                TABLE_SCHEMA = #{ data_base_name } AND TABLE_TYPE = 'BASE TABLE'
        </value>
    </sql>
    <sql>
        <key>GetModel</key>
        <value>
            SELECT
                TABLE_NAME, ENGINE, TABLE_COLLATION, TABLE_COMMENT, IFNULL(AUTO_INCREMENT, -1)
            FROM
                information_schema.TABLES
            WHERE
                TABLE_SCHEMA = #{ data_base_name } AND TABLE_TYPE = 'BASE TABLE'
                AND TABLE_NAME = #{ table_name }
        </value>
    </sql>
</xml>
"""

# noinspection SpellCheckingInspection
_column_xml = """
<xml>
    <mapper column="ORDINAL_POSITION" parameter="Number"/>
    <mapper column="COLUMN_NAME" parameter="Name"/>
    <mapper column="COLUMN_TYPE" parameter="Type"/>
    <mapper column="IS_NULLABLE" parameter="NullAble"/>
    <mapper column="COLUMN_DEFAULT" parameter="Defaule"/>
    <mapper column="COLUMN_COMMENT" parameter="Comment"/>
    <sql>
        <key>GetList</key>
        <value>
            SELECT
                ORDINAL_POSITION,
                COLUMN_NAME,
                COLUMN_TYPE,
                IS_NULLABLE,
                IFNULL(COLUMN_DEFAULT, ''),
                COLUMN_COMMENT
            FROM
                information_schema.COLUMNS
            WHERE
                TABLE_SCHEMA = #{ data_base_name } AND TABLE_NAME = #{ table_name }
        </value>
    </sql>
</xml>
"""

_index_xml = """
<xml>
    <mapper column="INDEX_NAME" parameter="Name"/>
    <mapper column="COLUMN_NAME" parameter="ColumnName"/>
    <mapper column="NON_UNIQUE" parameter="Unique"/>
    <mapper column="INDEX_TYPE" parameter="Type"/>
    <sql>
        <key>GetList</key>
        <value>
            SELECT
                INDEX_NAME,
                COLUMN_NAME,
                NON_UNIQUE,
                INDEX_TYPE
            FROM
                information_schema.STATISTICS
            WHERE
                TABLE_SCHEMA = #{ data_base_name } AND TABLE_NAME = #{ table_name }
        </value>
    </sql>
</xml>
"""

_key_xml = """
<xml>
    <mapper column="COLUMN_NAME" parameter="ColumnName"/>
    <mapper column="REFERENCED_TABLE_NAME" parameter="RelyTable"/>
    <mapper column="REFERENCED_COLUMN_NAME" parameter="RelyColumnName"/>
    <sql>
        <key>GetList</key>
        <value>
            SELECT
                COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM
                information_schema.KEY_COLUMN_USAGE
            WHERE
                CONSTRAINT_NAME != 'PRIMARY' AND
                TABLE_SCHEMA = REFERENCED_TABLE_SCHEMA AND
                TABLE_SCHEMA = #{ data_base_name } AND TABLE_NAME = #{ table_name }
        </value>
    </sql>
</xml>
"""

DatabaseInfoManager = Dict
DataBaseInfo = Dict


# noinspection SpellCheckingInspection
def get_db_info(database_info_manager: DatabaseInfoManager, database_name: str) -> DataBaseInfo:
    """
    Get database information
    :param database_info_manager: the database info manager
    :param database_name: Database name
    :return: database information
    """
    return __get_info(database_info_manager, "GetList", {"data_base_name": database_name})


# noinspection SpellCheckingInspection
def get_table_info(database_info_manager: DatabaseInfoManager, database_name: str, table_name: str) -> DataBaseInfo:
    """
    Get database information
    :param database_info_manager: the database info manager
    :param database_name: Database name
    :param table_name: database table name
    :return: database information
    """
    return __get_info(database_info_manager, "GetModel", {"data_base_name": database_name, "table_name": table_name})


def __get_info(database_info_manager: DatabaseInfoManager, query_name: str, query_param: dict) -> DataBaseInfo:
    """
    Get database information
    :param database_info_manager: the database info manager
    :param query_name: table manager query name
    :param query_param: table manager query name && query param
    :return: database information
    """
    # builder manager
    table_manager = database_info_manager["table_manager"]
    column_manager = database_info_manager["column_manager"]
    index_manager = database_info_manager["index_manager"]
    key_manager = database_info_manager["key_manager"]

    # Query table structure information
    tables = table_manager.query(query_name, query_param)
    for table in tables:
        table["columns"] = column_manager.query(
            "GetList",
            {"data_base_name": query_param["data_base_name"], "table_name": table["Name"]}
        )
        table["indexs"] = index_manager.query(
            "GetList",
            {"data_base_name": query_param["data_base_name"], "table_name": table["Name"]}
        )
        table["keys"] = key_manager.query(
            "GetList",
            {"data_base_name": query_param["data_base_name"], "table_name": table["Name"]}
        )
    return {"Name": query_param["data_base_name"], "tables": tables}
