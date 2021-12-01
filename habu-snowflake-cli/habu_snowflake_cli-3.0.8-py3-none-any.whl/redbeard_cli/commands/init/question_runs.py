from redbeard_cli import snowflake_utils


def install_handle_new_question_runs_controller_procedure(sf_connection):
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_NEW_QUESTION_RUNS() 
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var crRequestSql = "SELECT id AS request_id, request_data:clean_room_id AS clean_room_id, " +  
            " request_data:partner_account_id AS partner_account_id,  " + 
            " request_data:statement_hash AS statement_hash " + 
            " FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS " + 
            " WHERE request_type = :1 AND request_status = :2";
            var stmt = snowflake.createStatement({
                sqlText: crRequestSql,
                binds: ['NEW_QUESTION_RUN', 'PENDING']
            });
            
            var rs = stmt.execute();    
            var newQuestionRunParams = [];
            while (rs.next()) {
                var requestID = rs.getColumnValue(1);
                var cleanRoomID = rs.getColumnValue(2);
                var accountID = rs.getColumnValue(3);
                var statementHash = rs.getColumnValue(4);
                newQuestionRunParams.push({
                'rID': requestID, 'crID': cleanRoomID,
                'acID': accountID, 'sh': statementHash 
                })
            }
            
            for (var i = 0; i < newQuestionRunParams.length; i++){
                var stmt = snowflake.createStatement({
                    sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ADD_NEW_QUESTION_RUN(:1, :2, :3, :4)',
                    binds: [
                        newQuestionRunParams[i]['rID'], 
                        newQuestionRunParams[i]['crID'], 
                        newQuestionRunParams[i]['acID'],
                        newQuestionRunParams[i]['sh']
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


def install_add_new_question_run_procedure(sf_connection):
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ADD_NEW_QUESTION_RUN
    (REQUEST_ID VARCHAR, CLEAN_ROOM_ID VARCHAR, ACCOUNT_ID VARCHAR, STATEMENT_HASH VARCHAR)
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            snowflake.execute({
                sqlText: "INSERT INTO HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.ALLOWED_STATEMENTS (ACCOUNT_ID, CLEAN_ROOM_ID, STATEMENT_HASH) VALUES (:1, :2, :3)",
                binds: [ACCOUNT_ID, CLEAN_ROOM_ID, STATEMENT_HASH]
            })
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


def install_handle_new_question_runs_requester_procedure(sf_connection):
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_NEW_QUESTION_RUNS() 
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var crRequestSql = "SELECT id AS request_id, request_data:run_query AS run_query " +  
            " FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS " + 
            " WHERE request_type = :1 AND request_status = :2";
            var stmt = snowflake.createStatement({
                sqlText: crRequestSql,
                binds: ['NEW_QUESTION_RUN', 'PENDING']
            });
            
            var rs = stmt.execute();    
            var newQuestionRunParams = [];
            while (rs.next()) {
                var requestID = rs.getColumnValue(1);
                var runQuery = rs.getColumnValue(2);
                newQuestionRunParams.push({
                'rID': requestID, 'rq': runQuery 
                })
            }
            
            for (var i = 0; i < newQuestionRunParams.length; i++){
                var stmt = snowflake.createStatement({
                    sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.RUN_QUESTION(:1, :2)',
                    binds: [
                        newQuestionRunParams[i]['rID'], 
                        newQuestionRunParams[i]['rq']
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


def install_run_question_requester_procedure(sf_connection):
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.RUN_QUESTION
    (REQUEST_ID VARCHAR, QUESTION_RUN_QUERY VARCHAR)
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            snowflake.execute({sqlText: QUESTION_RUN_QUERY})
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
