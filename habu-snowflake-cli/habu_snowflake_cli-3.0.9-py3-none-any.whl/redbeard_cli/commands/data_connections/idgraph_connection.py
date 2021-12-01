import uuid

from redbeard_cli import snowflake_utils
from redbeard_cli.commands.data_connections import utils


def add_idgraph_data_connection(sf_connection, organization_id: str, db_name: str, db_schema: str,
                                db_table: str, parent_identity_type: str, parent_identity_column: str,
                                identity_type_column: str, identity_value_column: str):
    all_columns = [parent_identity_column, identity_type_column, identity_value_column]
    if not utils.validate_data_connection_request(sf_connection, db_name, db_schema, db_table, all_columns):
        return False

    snowflake_utils.run_query(
        sf_connection,
        "GRANT REFERENCE_USAGE ON DATABASE %s TO SHARE HABU_DATA_CONNECTIONS_SHARE" % db_name
    )

    dc_id = str(uuid.uuid4())
    snowflake_utils.run_query(
        sf_connection,
        """
        INSERT INTO HABU_DATA_CONNECTIONS.DATA_CONNECTIONS.DATA_CONNECTIONS 
        (ID, ORGANIZATION_ID, DATABASE_NAME, DB_SCHEMA_NAME, DB_TABLE_NAME, DATASET_TYPE)
        (
          SELECT :DCID:, :ORGID:, 
                 TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME, :DSTYPE:
          FROM %s.INFORMATION_SCHEMA.TABLES
          WHERE TABLE_CATALOG = :DBNAME: AND TABLE_SCHEMA = :DBSCHEMA: AND TABLE_NAME = :DBTABLE:
        )""" % db_name,
        [
            ("DCID", dc_id),
            ("ORGID", organization_id),
            ("DSTYPE", "IDENTITY_GRAPH"),
            ("DBNAME", db_name),
            ("DBSCHEMA", db_schema),
            ("DBTABLE", db_table),
        ]
    )

    snowflake_utils.run_query(
        sf_connection,
        """INSERT INTO HABU_DATA_CONNECTIONS.DATA_CONNECTIONS.DATA_CONNECTION_COLUMNS
        (ID, ORGANIZATION_ID, DATA_CONNECTION_ID, COLUMN_NAME, COLUMN_POSITION, DATA_TYPE, IS_LOOKUP_COLUMN, IS_IDENTITY_COLUMN)
        (
          SELECT uuid_string(), :ORGID:, :DCID:, 
          COLUMN_NAME, ORDINAL_POSITION, DATA_TYPE, FALSE, FALSE
          FROM %s.INFORMATION_SCHEMA.COLUMNS
          WHERE TABLE_CATALOG = :DBNAME: AND TABLE_SCHEMA = :DBSCHEMA: AND TABLE_NAME = :DBTABLE:  
        )""" % db_name,
        [
            ("ORGID", organization_id),
            ("DCID", dc_id),
            ("DBNAME", db_name),
            ("DBSCHEMA", db_schema),
            ("DBTABLE", db_table)
        ]
    )

    for column in [parent_identity_column, identity_value_column]:
        snowflake_utils.run_query(
            sf_connection,
            """UPDATE HABU_DATA_CONNECTIONS.DATA_CONNECTIONS.DATA_CONNECTION_COLUMNS 
            SET IS_IDENTITY_COLUMN = TRUE 
            WHERE DATA_CONNECTION_ID = :DCID: AND ORGANIZATION_ID = :ORGID: 
            AND COLUMN_NAME = :DBCOLUMN:""",
            [
                ("DCID", dc_id),
                ("ORGID", organization_id),
                ("DBCOLUMN", column.upper())
            ]
        )

    snowflake_utils.run_query(
        sf_connection,
        """
        INSERT INTO HABU_DATA_CONNECTIONS.DATA_CONNECTIONS.IDGRAPH_DATA_CONNECTION_INFO 
        (ORGANIZATION_ID, DATA_CONNECTION_ID, PARENT_ID_TYPE, PARENT_ID_COLUMN, 
        IDENTITY_TYPE_COLUMN, IDENTITY_VALUE_COLUMN) 
        VALUES (:ORGID:, :DCID:, :PID_TYPE:, :PID_COLUMN:, :IDT:, :IDV:)""",
        [
            ("ORGID", organization_id),
            ("DCID", dc_id),
            ("PID_TYPE", parent_identity_type),
            ("PID_COLUMN", parent_identity_column),
            ("IDT", identity_type_column),
            ("IDV", identity_value_column)
        ]
    )
