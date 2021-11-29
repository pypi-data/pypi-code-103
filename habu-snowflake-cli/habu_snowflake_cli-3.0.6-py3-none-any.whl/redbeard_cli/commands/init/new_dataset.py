from redbeard_cli import snowflake_utils


def install_handle_new_datasets_procedure(sf_connection):
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_NEW_DATASETS() 
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var crRequestSql = "SELECT id AS request_id, request_data:clean_room_id AS clean_room_id, " + 
            " request_data:id_graph_type AS id_graph_type, " + 
            " request_data:source_db AS source_db, " + 
            " request_data:view_name AS view_name, request_data:view_sql AS view_sql, " + 
            " request_data:available_values_sql AS available_values_sql, " + 
            " request_data:dc_id_type AS dc_id_type, request_data:dc_id_column AS dc_id_column " + 
            " FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS " + 
            " WHERE request_type = :1 AND request_status = :2";
            var stmt = snowflake.createStatement({
                sqlText: crRequestSql,
                binds: ['NEW_DATASET', 'PENDING']
            });
            
            var rs = stmt.execute();    
            var newDatasetParams = [];
            while (rs.next()) {
                var requestID = rs.getColumnValue(1);
                var cleanRoomID = rs.getColumnValue(2);
                var idGraphType = rs.getColumnValue(3);
                var sourceDB = rs.getColumnValue(4);
                var viewName = rs.getColumnValue(5);
                var viewSql = rs.getColumnValue(6);
                var availableValuesSql = rs.getColumnValue(7);
                var dcIdType = rs.getColumnValue(8);
                var dcIdColumn = rs.getColumnValue(9);
                newDatasetParams.push({
                'rID': requestID, 'crID': cleanRoomID, 
                'idgt': idGraphType, 'sourceDB': sourceDB, 
                'vn': viewName, 'vs': viewSql,
                'avs': availableValuesSql,
                'dcidt': dcIdType, 'dcidc': dcIdColumn 
                })
            }
            
            for (var i = 0; i < newDatasetParams.length; i++){
                var stmt = snowflake.createStatement({
                    sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CREATE_NEW_DATASET(:1, :2, :3, :4, :5, :6, :7, :8, :9)',
                    binds: [
                        newDatasetParams[i]['rID'], 
                        newDatasetParams[i]['crID'], 
                        newDatasetParams[i]['idgt'], 
                        newDatasetParams[i]['sourceDB'], 
                        newDatasetParams[i]['vn'], 
                        newDatasetParams[i]['vs'],
                        newDatasetParams[i]['avs'],
                        newDatasetParams[i]['dcidt'],
                        newDatasetParams[i]['dcidc']
                    ]
                });        
                stmt.execute();
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
    $$;"""
    snowflake_utils.run_query(sf_connection, sp_sql)


def install_create_new_dataset_procedure(sf_connection):
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CREATE_NEW_DATASET
    (REQUEST_ID VARCHAR, CLEAN_ROOM_ID VARCHAR, IDGRAPH_TYPE VARCHAR, SOURCE_DB VARCHAR, VIEW_NAME VARCHAR, VIEW_SQL VARCHAR, 
    AVAILABLE_VALUES_SQL VARCHAR, DC_ID_TYPE VARCHAR, DC_ID_COLUMN VARCHAR)
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var sf_clean_room_id = CLEAN_ROOM_ID.replace(/-/g, '').toUpperCase();
            snowflake.execute({
                sqlText: "GRANT REFERENCE_USAGE ON DATABASE " + SOURCE_DB + " TO SHARE HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE"
            })
            snowflake.execute({
                sqlText: "GRANT REFERENCE_USAGE ON DATABASE " + SOURCE_DB + " TO SHARE HABU_CR_PROVIDER_" + sf_clean_room_id + "_HABU_SHARE"
            })
            snowflake.execute({
                sqlText: "GRANT REFERENCE_USAGE ON DATABASE HABU_DATA_CONNECTIONS  TO SHARE HABU_CR_PROVIDER_" + sf_clean_room_id + "_HABU_SHARE"
            })
    
            snowflake.execute({sqlText: VIEW_SQL});
            if (AVAILABLE_VALUES_SQL !== "NONE") {
                snowflake.execute({sqlText: AVAILABLE_VALUES_SQL});
            }
            
            if (IDGRAPH_TYPE === "habu") {
                if (DC_ID_TYPE === "MAID") {
                    var idGraphTable = "MAID_ID_GRAPH";
                    var idGraphColumn = "MAID";
                    var viewIdJoinColumn = "T2." + DC_ID_COLUMN;
                } else {
                    var idGraphTable = "EMAIL_ID_GRAPH";
                    if (DC_ID_TYPE === "SHA1") {
                        var idGraphColumn = "EMAIL_SHA1";
                        var viewIdJoinColumn = "T2." + DC_ID_COLUMN;
                    } else if (DC_ID_TYPE === "SHA256") {
                        var idGraphColumn = "EMAIL_SHA256";
                        var viewIdJoinColumn = "T2." + DC_ID_COLUMN;
                    } else if (DC_ID_TYPE === "MD5") {
                        var idGraphColumn = "EMAIL_MD5";
                        var viewIdJoinColumn = "T2." + DC_ID_COLUMN;
                    } else if (DC_ID_TYPE === "Email") {
                        var idGraphColumn = "EMAIL_SHA256";
                        var viewIdJoinColumn = "T2." + DC_ID_COLUMN;
                    } else if (DC_ID_TYPE === "Email") {
                        var idGraphColumn = "EMAIL_SHA256";
                        var viewIdJoinColumn = "SHA2(T2." + DC_ID_COLUMN + ")";
                    } else {
                        var idGraphTable = "NONE";
                    }
                }
                
                if (idGraphTable !== "NONE") {
                    var orgUserIdentitiesSql = "INSERT INTO HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM.ORG_USER_IDENTITIES " + 
                    "(CLEAN_ROOM_ID, ID_TYPE, ID_VALUE, HABU_USER_ID) (SELECT :1 AS CLEAN_ROOM_ID, :2 AS ID_TYPE, T1." + idGraphColumn + " AS ID_VALUE, " + 
                    "SHA2(CONCAT(CAST(T1.PERSON_ID AS VARCHAR), :3)) AS HABU_USER_ID " + 
                    "FROM HABU_ID_GRAPH_SHARE_DB.PUBLIC." + idGraphTable + " T1, " + 
                    "(SELECT DISTINCT " + DC_ID_COLUMN + " FROM HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + ")T2 " + 
                    "WHERE T1." + idGraphColumn + " = T2." + DC_ID_COLUMN + 
                    " AND NOT EXISTS (SELECT 1 FROM HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM.ORG_USER_IDENTITIES TX " + 
                    " WHERE TX.ID_TYPE = :4 AND TX.ID_VALUE = T2." + DC_ID_COLUMN + "))";
                    
                    snowflake.execute({
                        sqlText: orgUserIdentitiesSql,
                        binds: [CLEAN_ROOM_ID, DC_ID_TYPE, CLEAN_ROOM_ID, DC_ID_TYPE]
                    });
                }
            }
    
            var policySql = "CREATE OR REPLACE ROW ACCESS POLICY HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + "_POLICY AS (query_clean_room_id VARCHAR) " + 
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
                sqlText: "ALTER VIEW HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + " ADD ROW ACCESS POLICY HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + "_POLICY ON (clean_room_id)"
            });
            
            snowflake.execute({
                sqlText: "GRANT SELECT ON VIEW HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + " TO SHARE HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE"
            });
            
            if (AVAILABLE_VALUES_SQL !== "NONE") {
                snowflake.execute({
                    sqlText: "GRANT SELECT ON VIEW HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + "_AVAILABLE_VALUES TO SHARE HABU_CR_PROVIDER_" + sf_clean_room_id + "_HABU_SHARE"
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
    $$;"""
    snowflake_utils.run_query(sf_connection, sp_sql)


def install_handle_new_requester_datasets_procedure(sf_connection):
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_NEW_REQUESTER_DATASETS() 
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        var crRequestSql = "SELECT id AS request_id, request_data:clean_room_id AS clean_room_id, " + 
        " request_data:id_graph_type AS id_graph_type, " + 
        " request_data:source_db AS source_db, " + 
        " request_data:view_name AS view_name, request_data:view_sql AS view_sql, " + 
        " request_data:available_values_sql AS available_values_sql, " + 
        " request_data:dc_id_type AS dc_id_type, request_data:dc_id_column AS dc_id_column " + 
        " FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS " + 
        " WHERE request_type = :1 AND request_status = :2";
        var stmt = snowflake.createStatement({
            sqlText: crRequestSql,
            binds: ['NEW_DATASET', 'PENDING']
        });
        
        var rs = stmt.execute();    
        var newDatasetParams = [];
        while (rs.next()) {
            var requestID = rs.getColumnValue(1);
            var cleanRoomID = rs.getColumnValue(2);
            var idGraphType = rs.getColumnValue(3);
            var sourceDB = rs.getColumnValue(4);
            var viewName = rs.getColumnValue(5);
            var viewSql = rs.getColumnValue(6);
            var availableValuesSql = rs.getColumnValue(7);
            var dcIdType = rs.getColumnValue(8);
            var dcIdColumn = rs.getColumnValue(9);
            newDatasetParams.push({
            'rID': requestID, 'crID': cleanRoomID, 
            'idgt': idGraphType, 'sourceDB': sourceDB, 
            'vn': viewName, 'vs': viewSql,
            'avs': availableValuesSql,
            'dcidt': dcIdType, 'dcidc': dcIdColumn 
            })
        }
        
        for (var i = 0; i < newDatasetParams.length; i++){
            var stmt = snowflake.createStatement({
                sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CREATE_NEW_REQUESTER_DATASET(:1, :2, :3, :4, :5, :6, :7, :8, :9)',
                binds: [
                    newDatasetParams[i]['rID'], 
                    newDatasetParams[i]['crID'], 
                    newDatasetParams[i]['idgt'], 
                    newDatasetParams[i]['sourceDB'], 
                    newDatasetParams[i]['vn'], 
                    newDatasetParams[i]['vs'],
                    newDatasetParams[i]['avs'],
                    newDatasetParams[i]['dcidt'],
                    newDatasetParams[i]['dcidc']
                ]
            });        
            stmt.execute();
        }        
        return "SUCCESS";
    $$;"""
    snowflake_utils.run_query(sf_connection, sp_sql)


def install_create_new_requester_dataset_procedure(sf_connection):
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CREATE_NEW_REQUESTER_DATASET
    (REQUEST_ID VARCHAR, CLEAN_ROOM_ID VARCHAR, IDGRAPH_TYPE VARCHAR, SOURCE_DB VARCHAR, VIEW_NAME VARCHAR, VIEW_SQL VARCHAR, 
    AVAILABLE_VALUES_SQL VARCHAR, DC_ID_TYPE VARCHAR, DC_ID_COLUMN VARCHAR)
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var sf_clean_room_id = CLEAN_ROOM_ID.replace(/-/g, '').toUpperCase();
            snowflake.execute({
                sqlText: "GRANT REFERENCE_USAGE ON DATABASE " + SOURCE_DB + " TO SHARE HABU_CR_REQUESTER_" + sf_clean_room_id + "_HABU_SHARE"
            })
            snowflake.execute({
                sqlText: "GRANT REFERENCE_USAGE ON DATABASE HABU_DATA_CONNECTIONS  TO SHARE HABU_CR_REQUESTER_" + sf_clean_room_id + "_HABU_SHARE"
            })
    
            snowflake.execute({sqlText: VIEW_SQL});
            if (AVAILABLE_VALUES_SQL !== "NONE") {
                snowflake.execute({sqlText: AVAILABLE_VALUES_SQL});
            }
             
            if (IDGRAPH_TYPE === "habu") {
                if (DC_ID_TYPE === "MAID") {
                    var idGraphTable = "MAID_ID_GRAPH";
                    var idGraphColumn = "MAID";
                    var viewIdJoinColumn = "T2." + DC_ID_COLUMN;
                } else {
                    var idGraphTable = "EMAIL_ID_GRAPH";
                    if (DC_ID_TYPE === "SHA1") {
                        var idGraphColumn = "EMAIL_SHA1";
                        var viewIdJoinColumn = "T2." + DC_ID_COLUMN;
                    } else if (DC_ID_TYPE === "SHA256") {
                        var idGraphColumn = "EMAIL_SHA256";
                        var viewIdJoinColumn = "T2." + DC_ID_COLUMN;
                    } else if (DC_ID_TYPE === "MD5") {
                        var idGraphColumn = "EMAIL_MD5";
                        var viewIdJoinColumn = "T2." + DC_ID_COLUMN;
                    } else if (DC_ID_TYPE === "Email") {
                        var idGraphColumn = "EMAIL_SHA256";
                        var viewIdJoinColumn = "T2." + DC_ID_COLUMN;
                    } else if (DC_ID_TYPE === "Email") {
                        var idGraphColumn = "EMAIL_SHA256";
                        var viewIdJoinColumn = "T2." + DC_ID_COLUMN;
                    } else {
                        var idGraphTable = "NONE";
                    }
                }
                
                if (idGraphTable !== "NONE") {
                    var orgUserIdentitiesSql = "INSERT INTO HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM.ORG_USER_IDENTITIES " + 
                    "(CLEAN_ROOM_ID, ID_TYPE, ID_VALUE, HABU_USER_ID) (SELECT :1 AS CLEAN_ROOM_ID, :2 AS ID_TYPE, T1." + idGraphColumn + " AS ID_VALUE, " + 
                    "SHA2(CONCAT(CAST(T1.PERSON_ID AS VARCHAR), :3)) AS HABU_USER_ID " + 
                    "FROM HABU_ID_GRAPH_SHARE_DB.PUBLIC." + idGraphTable + " T1, " + 
                    "(SELECT DISTINCT " + DC_ID_COLUMN + " FROM HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + ")T2 " + 
                    "WHERE T1." + idGraphColumn + " = " + viewIdJoinColumn + 
                    " AND NOT EXISTS (SELECT 1 FROM HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM.ORG_USER_IDENTITIES TX " + 
                    " WHERE TX.ID_TYPE = :4 AND TX.ID_VALUE = T2." + DC_ID_COLUMN + "))";
                    
                    snowflake.execute({
                        sqlText: orgUserIdentitiesSql,
                        binds: [CLEAN_ROOM_ID, DC_ID_TYPE, CLEAN_ROOM_ID, DC_ID_TYPE]
                    });
                } 
            }         
            
            if (AVAILABLE_VALUES_SQL !== "NONE") {
                snowflake.execute({
                    sqlText: "GRANT SELECT ON VIEW HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM." + VIEW_NAME + "_AVAILABLE_VALUES TO SHARE HABU_CR_REQUESTER_" + sf_clean_room_id + "_HABU_SHARE"
                });
            }
    
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
    $$;"""
    snowflake_utils.run_query(sf_connection, sp_sql)
