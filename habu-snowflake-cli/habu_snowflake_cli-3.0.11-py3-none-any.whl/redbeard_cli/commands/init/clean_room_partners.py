from redbeard_cli import snowflake_utils


def install_handle_new_clean_room_partners_procedure(sf_connection):
    """
    Install stored procedure that will handle all requests to add a new partner
    to an existing clean room.  Currently, this assumes that the clean room already exists
    and all the requisite Snowflake objects associated with that clean room have
    been created by the NEW_CLEAN_ROOOM stored procedure

    :param sf_connection: the Snowflake connection object used to communicate with Snowflake
    :return:
    """
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_NEW_CLEAN_ROOM_PARTNERS()
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var crRequestSql = "SELECT id AS request_id, request_data:clean_room_id AS clean_room_id, request_data:partner_account_id AS partner_account_id FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS WHERE request_type = :1 AND request_status = :2 ORDER BY CREATED_AT ASC";
            var stmt = snowflake.createStatement({
                sqlText: crRequestSql,
                binds: ['NEW_CLEAN_ROOM_PARTNER', 'PENDING']
            });
            
            var rs = stmt.execute();    
            var requestParams = [];
            while (rs.next()) {
                var requestID = rs.getColumnValue(1)
                var cleanRoomID = rs.getColumnValue(2);
                var partnerAccountID = rs.getColumnValue(3).toUpperCase();
                requestParams.push({
                'rID': requestID,
                'crID': cleanRoomID, 
                'pacID': partnerAccountID
                })
            }
            
            for (var i = 0; i < requestParams.length; i++){
                var stmt = snowflake.createStatement({
                    sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ADD_NEW_CLEAN_ROOM_PARTNER(:1, :2, :3)',
                    binds: [
                        requestParams[i]['rID'],
                        requestParams[i]['crID'], 
                        requestParams[i]['pacID']
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


def install_new_clean_room_partner_stored_procedure(sf_connection):
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ADD_NEW_CLEAN_ROOM_PARTNER 
    (REQUEST_ID VARCHAR, CLEAN_ROOM_ID VARCHAR, PARTNER_ACCOUNT_ID VARCHAR)
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var sf_clean_room_id = CLEAN_ROOM_ID.replace(/-/g, '').toUpperCase();        
            snowflake.execute({
                sqlText: "ALTER SHARE HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE ADD ACCOUNTS = :1",
                binds: [PARTNER_ACCOUNT_ID]
            });
            
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
    """
    snowflake_utils.run_query(sf_connection, sp_sql)


def install_handle_accept_clean_room_invitations_procedure(sf_connection):
    """
    Install stored procedure that will handle all requests to accept clean room invitations
    in a requester account. The provider will have triggered a share called
    HABU_CR_{CLEAN_ROOM_ID}_PARTNER_SHARE where {CLEAN_ROOM_ID} is Snowflake version
    of the Clean Room ID from the Habu platform [clean_room_id.replace('-', '').upper()]

    :param sf_connection: the Snowflake connection object used to communicate with Snowflake
    :return:
    """
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_ACCEPT_CLEAN_ROOM_INVITATIONS()
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var crRequestSql = "SELECT id AS request_id, request_data:clean_room_id AS clean_room_id, request_data:requester_account_id AS requester_account_id, request_data:provider_account_id AS provider_account_id, request_data:habu_account_id AS habu_account_id FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS WHERE request_type = :1 AND request_status = :2 ORDER BY CREATED_AT ASC";
            var stmt = snowflake.createStatement({
                sqlText: crRequestSql,
                binds: ['CLEAN_ROOM_INVITATION', 'PENDING']
            });
            
            var rs = stmt.execute();    
            var requestParams = [];
            while (rs.next()) {
                var requestID = rs.getColumnValue(1)
                var cleanRoomID = rs.getColumnValue(2);
                var requesterAccountID = rs.getColumnValue(3).toUpperCase();
                var providerAccountID = rs.getColumnValue(4).toUpperCase();
                var habuAccountID = rs.getColumnValue(5).toUpperCase();
                requestParams.push({
                'rID': requestID,
                'crID': cleanRoomID, 
                'racID': requesterAccountID,
                'pacID': providerAccountID,
                'hacID': habuAccountID
                })
            }
            
            for (var i = 0; i < requestParams.length; i++){
                var stmt = snowflake.createStatement({
                    sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ACCEPT_CLEAN_ROOM_INVITATION(:1, :2, :3, :4, :5)',
                    binds: [
                        requestParams[i]['rID'],
                        requestParams[i]['crID'],
                        requestParams[i]['racID'], 
                        requestParams[i]['pacID'],
                        requestParams[i]['hacID']
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


def install_accept_clean_room_invitation_stored_procedure(sf_connection, share_restrictions: bool):
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ACCEPT_CLEAN_ROOM_INVITATION
    (REQUEST_ID VARCHAR, CLEAN_ROOM_ID VARCHAR, REQUESTER_ACCOUNT_ID VARCHAR, PARTNER_ACCOUNT_ID VARCHAR, HABU_ACCOUNT_ID VARCHAR)
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var sf_clean_room_id = CLEAN_ROOM_ID.replace(/-/g, '').toUpperCase();
            snowflake.execute({
                sqlText: "CREATE DATABASE HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE_DB FROM SHARE " + PARTNER_ACCOUNT_ID + ".HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE COMMENT = 'HABU_" + REQUESTER_ACCOUNT_ID + "'"
            });
            snowflake.execute({
                sqlText: "GRANT IMPORTED PRIVILEGES ON DATABASE HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE_DB TO ROLE ACCOUNTADMIN"
            })
            snowflake.execute({
                sqlText: "GRANT IMPORTED PRIVILEGES ON DATABASE HABU_CR_" + sf_clean_room_id + "_PARTNER_SHARE_DB TO ROLE SYSADMIN"
            })
            
            snowflake.execute({
                sqlText: "CREATE DATABASE IF NOT EXISTS HABU_CLEAN_ROOM_" + sf_clean_room_id + " COMMENT = 'HABU_" + REQUESTER_ACCOUNT_ID + "'"
            });
        
            snowflake.execute({
                sqlText: "CREATE SCHEMA IF NOT EXISTS HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM COMMENT = 'HABU_" + REQUESTER_ACCOUNT_ID + "'"
            });
        
            snowflake.execute({
                sqlText: "CREATE SCHEMA IF NOT EXISTS HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM_RUN_RESULTS COMMENT = 'HABU_" + REQUESTER_ACCOUNT_ID + "'"
            });
    
            snowflake.execute({
                sqlText: "CREATE OR REPLACE SHARE HABU_CR_REQUESTER_" + sf_clean_room_id + "_HABU_SHARE"
            });
        
            snowflake.execute({
                sqlText: "GRANT USAGE ON DATABASE HABU_CLEAN_ROOM_" + sf_clean_room_id + " TO SHARE HABU_CR_REQUESTER_" + sf_clean_room_id + "_HABU_SHARE"
            });
        
            snowflake.execute({
                sqlText: "GRANT USAGE ON SCHEMA HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM TO SHARE HABU_CR_REQUESTER_" + sf_clean_room_id + "_HABU_SHARE"
            });
        
            snowflake.execute({
                sqlText: "GRANT USAGE ON SCHEMA HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM_RUN_RESULTS TO SHARE HABU_CR_REQUESTER_" + sf_clean_room_id + "_HABU_SHARE"
            });
    
            snowflake.execute({
                sqlText: "ALTER SHARE HABU_CR_REQUESTER_" + sf_clean_room_id + "_HABU_SHARE ADD ACCOUNTS = :1 SHARE_RESTRICTIONS=%s",
                binds: [HABU_ACCOUNT_ID]
            });
            
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