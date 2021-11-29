from redbeard_cli import snowflake_utils


def install_handle_new_clean_rooms_procedure(sf_connection):
    """
    Install stored procedure that will handle all new clean room creation requests
    that are present in the HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS table.

    :param sf_connection: the Snowflake connection object used to communicate with Snowflake
    :return:
    """
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_NEW_CLEAN_ROOMS()
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var crRequestSql = "SELECT id AS request_id, request_data:clean_room_id AS clean_room_id, request_data:account_id AS account_id, request_data:habu_account_id AS habu_account_id, request_data:id_graph_type AS id_graph_type, request_data:id_graph_source_db AS id_graph_source_db, request_data:id_graph_view_sql AS id_graph_view_sql  FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS WHERE request_type = :1 AND request_status = :2";
            var stmt = snowflake.createStatement({
                sqlText: crRequestSql,
                binds: ['NEW_CLEAN_ROOM', 'PENDING']
            });
            
            var rs = stmt.execute();    
            var newCleanRoomRequestParams = [];
            while (rs.next()) {
                var requestID = rs.getColumnValue(1)
                var cleanRoomID = rs.getColumnValue(2);
                var accountID = rs.getColumnValue(3).toUpperCase();
                var habuAccountID = rs.getColumnValue(4).toUpperCase();
                var idGraphType = rs.getColumnValue(5);
                var idGraphSourceDb = rs.getColumnValue(6);
                var idGraphViewSql = rs.getColumnValue(7);

                
                newCleanRoomRequestParams.push({
                    'rID': requestID,
                    'crID': cleanRoomID, 
                    'acID': accountID, 
                    'hacID': habuAccountID,
                    'idGT': idGraphType,
                    'idGSDB': idGraphSourceDb,
                    'idGVS': idGraphViewSql,
                })
            }
            
            for (var i = 0; i < newCleanRoomRequestParams.length; i++){
                var stmt = snowflake.createStatement({
                    sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CREATE_NEW_CLEAN_ROOM(:1, :2, :3, :4, :5, :6, :7)',
                    binds: [
                        newCleanRoomRequestParams[i]['rID'],
                        newCleanRoomRequestParams[i]['crID'], 
                        newCleanRoomRequestParams[i]['acID'], 
                        newCleanRoomRequestParams[i]['hacID'],
                        newCleanRoomRequestParams[i]['idGT'],
                        newCleanRoomRequestParams[i]['idGSDB'],
                        newCleanRoomRequestParams[i]['idGVS']
                    ]
                });        
                var res = stmt.execute();
                
            }        
            result = "SUCCESS";
        } catch (err) {
            result = "FAILED";
            var stmt = snowflake.createStatement({
                sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_ERROR(:1, :2, :3, :4, :5, :6)',
                binds: [
                    err.code, err.state, err.message, err.stackTraceTxt, "", Object.keys(this)[0]
                ]
            });        
            var res = stmt.execute();
        }
        return result;
    $$;
    """
    snowflake_utils.run_query(sf_connection, sp_sql)


def install_new_clean_room_stored_procedure(sf_connection, share_restrictions: bool):
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CREATE_NEW_CLEAN_ROOM 
    (REQUEST_ID VARCHAR, CLEAN_ROOM_ID VARCHAR, CUSTOMER_ACCOUNT_ID VARCHAR, HABU_ACCOUNT_ID VARCHAR, IDGRAPH_TYPE VARCHAR, ID_GRAPH_SOURCE_DB VARCHAR, IDGRAPH_SQL VARCHAR)
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$        
        try {
            var sf_clean_room_id = CLEAN_ROOM_ID.replace(/-/g, '').toUpperCase();
            snowflake.execute({
                sqlText: "CREATE DATABASE IF NOT EXISTS HABU_CLEAN_ROOM_" + sf_clean_room_id + " COMMENT = 'HABU_" + CUSTOMER_ACCOUNT_ID + "'"
            });
        
            snowflake.execute({
                sqlText: "CREATE SCHEMA IF NOT EXISTS HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM COMMENT = 'HABU_" + CUSTOMER_ACCOUNT_ID + "'"
            });
        
            snowflake.execute({
                sqlText: "CREATE TABLE IF NOT EXISTS HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM.ORG_USER_IDENTITIES (CLEAN_ROOM_ID VARCHAR(40), ID_TYPE VARCHAR(20) NOT NULL, ID_VALUE VARCHAR(255) NOT NULL, HABU_USER_ID VARCHAR(64) NOT NULL)"
            });
        
            snowflake.execute({
                sqlText: "ALTER TABLE HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM.ORG_USER_IDENTITIES ADD ROW ACCESS POLICY HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ORG_USER_IDENTITIES_POLICY ON (ID_VALUE)"
            });
        
            snowflake.execute({
                sqlText: "CREATE OR REPLACE SHARE HABU_CR_PROVIDER_" + sf_clean_room_id + "_HABU_SHARE"
            });
        
            snowflake.execute({
                sqlText: "GRANT USAGE ON DATABASE HABU_CLEAN_ROOM_" + sf_clean_room_id + " TO SHARE HABU_CR_PROVIDER_" + sf_clean_room_id + "_HABU_SHARE"
            });
        
            snowflake.execute({
                sqlText: "GRANT USAGE ON SCHEMA HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM TO SHARE HABU_CR_PROVIDER_" + sf_clean_room_id + "_HABU_SHARE"
            });
        
            snowflake.execute({
                sqlText: "ALTER SHARE HABU_CR_PROVIDER_" + sf_clean_room_id + "_HABU_SHARE ADD ACCOUNTS = :1 SHARE_RESTRICTIONS=%s",
                binds: [HABU_ACCOUNT_ID]
            });
            
            snowflake.execute({
                sqlText: "CREATE OR REPLACE SHARE HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE" 
            });
            
            snowflake.execute({
                sqlText: "GRANT USAGE ON DATABASE HABU_CLEAN_ROOM_" + sf_clean_room_id + " TO SHARE HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE"
            });
            snowflake.execute({
                sqlText: "GRANT USAGE ON SCHEMA HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM TO SHARE HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE"
            });
            
            snowflake.execute({
                sqlText: "CREATE OR REPLACE SECURE VIEW HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM.V_ALLOWED_STATEMENTS " + 
                " AS SELECT CLEAN_ROOM_ID, ACCOUNT_ID, STATEMENT_HASH FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ALLOWED_STATEMENTS " + 
                " WHERE account_id = CURRENT_ACCOUNT() AND clean_room_id = '" + CLEAN_ROOM_ID + "'"
            });
            
            snowflake.execute({
                sqlText: "GRANT REFERENCE_USAGE ON DATABASE HABU_CLEAN_ROOM_COMMON TO SHARE HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE"
            });
            
            snowflake.execute({
                sqlText: "GRANT SELECT ON VIEW HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM.V_ALLOWED_STATEMENTS TO SHARE HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE"
            });
            
            snowflake.execute({
                sqlText: "GRANT SELECT ON TABLE HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM.ORG_USER_IDENTITIES TO SHARE HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE"
            });
            
            if(IDGRAPH_TYPE === "custom") {
                snowflake.execute({
                    sqlText: IDGRAPH_SQL
                });
                
                snowflake.execute({
                    sqlText: "GRANT REFERENCE_USAGE ON DATABASE " + ID_GRAPH_SOURCE_DB +" TO SHARE HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE"
                });
                
                snowflake.execute({
                    sqlText: "GRANT SELECT ON VIEW HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM.V_ID_GRAPH TO SHARE HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE"
                });
                
                var policySql = "CREATE OR REPLACE ROW ACCESS POLICY HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM.V_ID_GRAPH_POLICY AS (query_clean_room_id VARCHAR) " + 
                "RETURNS BOOLEAN -> " + 
                "CASE " + 
                " WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'SYSADMIN') THEN TRUE " + 
                " WHEN EXISTS (SELECT 1 FROM HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM.V_ALLOWED_STATEMENTS WHERE " + 
                " account_id = CURRENT_ACCOUNT() AND statement_hash = SHA2(CURRENT_STATEMENT()) " + 
                " AND clean_room_id = QUERY_CLEAN_ROOM_ID) " + 
                " THEN TRUE END;";
    
                var policyStmt = snowflake.createStatement({sqlText: policySql});
                policyStmt.execute();

                snowflake.execute({
                    sqlText: "ALTER VIEW HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM.V_ID_GRAPH ADD ROW ACCESS POLICY HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM.V_ID_GRAPH_POLICY ON (clean_room_id)"
                });
        
            }
    
            snowflake.execute({
                sqlText: "UPDATE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS SET REQUEST_STATUS = :1, UPDATED_AT = CURRENT_TIMESTAMP() WHERE ID = :2",
                binds: ['COMPLETE', REQUEST_ID]
            });
                    
            result = "SUCCESS";
        } catch (err) {
            result = "FAILED";
            var stmt = snowflake.createStatement({
                sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_ERROR(:1, :2, :3, :4, :5, :6)',
                binds: [
                    err.code, err.state, err.message, err.stackTraceTxt, REQUEST_ID, Object.keys(this)[0]
                ]
            });        
            var res = stmt.execute();
        }
        return result;
    $$;
    """ % share_restrictions
    snowflake_utils.run_query(sf_connection, sp_sql)


def install_add_clean_room_partner_stored_procedure(sf_connection):
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ADD_CLEAN_ROOM_PARTNER 
    (REQUEST_ID VARCHAR, CLEAN_ROOM_ID VARCHAR, PARTNER_ACCOUNT_ID VARCHAR)
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$    
        try {    
            snowflake.execute({
                sqlText: "ALTER SHARE HABU_CR_" + CLEAN_ROOM_ID + "_PARTNER_SHARE ADD ACCOUNTS = :1",
                binds: [PARTNER_ACCOUNT_ID] 
            })
            
            snowflake.execute({
                sqlText: "UPDATE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS SET REQUEST_STATUS = :1, UPDATED_AT = CURRENT_TIMESTAMP() WHERE ID = :2",
                binds: ['COMPLETE', REQUEST_ID]
            })
            result = "SUCCESS";
        } catch (err) {
            result = "FAILED";
            var stmt = snowflake.createStatement({
                sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_ERROR(:1, :2, :3, :4, :5, :6)',
                binds: [
                    err.code, err.state, err.message, err.stackTraceTxt, REQUEST_ID, Object.keys(this)[0]
                ]
            });        
            var res = stmt.execute();
        }
        return result;
    $$;
    """
    snowflake_utils.run_query(sf_connection, sp_sql)
