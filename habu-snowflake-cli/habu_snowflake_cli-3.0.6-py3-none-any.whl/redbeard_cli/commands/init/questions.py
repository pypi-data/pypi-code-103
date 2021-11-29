from redbeard_cli import snowflake_utils


def install_handle_new_questions_procedure(sf_connection):
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.HANDLE_NEW_QUESTIONS() 
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var crRequestSql = "SELECT id AS request_id, request_data:clean_room_id AS clean_room_id,  " + 
            " request_data:result_table AS result_table, " + 
            " request_data:result_table_ddl AS result_table_ddl " + 
            " FROM HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CLEAN_ROOM_REQUESTS " + 
            " WHERE request_type = :1 AND request_status = :2";
            var stmt = snowflake.createStatement({
                sqlText: crRequestSql,
                binds: ['NEW_QUESTION', 'PENDING']
            });
            
            var rs = stmt.execute();    
            var newQuestionParams = [];
            while (rs.next()) {
                var requestID = rs.getColumnValue(1);
                var cleanRoomID = rs.getColumnValue(2);
                var resultTable = rs.getColumnValue(3);
                var resultTableDDL = rs.getColumnValue(4);
                newQuestionParams.push({
                'rID': requestID,'crID': cleanRoomID, 
                'rt': resultTable, 'rtd': resultTableDDL 
                })
            }
            
            for (var i = 0; i < newQuestionParams.length; i++){
                var stmt = snowflake.createStatement({
                    sqlText: 'CALL HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CREATE_NEW_QUESTION(:1, :2, :3, :4)',
                    binds: [
                        newQuestionParams[i]['rID'], 
                        newQuestionParams[i]['crID'],
                        newQuestionParams[i]['rt'],
                        newQuestionParams[i]['rtd']
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


def install_create_new_question_procedure(sf_connection):
    sp_sql = """
    CREATE OR REPLACE PROCEDURE HABU_CLEAN_ROOM_COMMON.CLEAN_ROOM.CREATE_NEW_QUESTION
    (REQUEST_ID VARCHAR, CLEAN_ROOM_ID VARCHAR, RESULT_TABLE VARCHAR, RESULT_TABLE_DDL VARCHAR)
    RETURNS STRING
    LANGUAGE JAVASCRIPT
    STRICT
    EXECUTE AS OWNER
    AS
    $$
        try {
            var sf_clean_room_id = CLEAN_ROOM_ID.replace(/-/g, '').toUpperCase();
            snowflake.execute({
                sqlText: RESULT_TABLE_DDL 
            });
            snowflake.execute({
                sqlText: "GRANT SELECT ON TABLE HABU_CLEAN_ROOM_" + sf_clean_room_id + ".CLEAN_ROOM_RUN_RESULTS." + RESULT_TABLE + " TO SHARE HABU_CR_REQUESTER_" + sf_clean_room_id + "_HABU_SHARE"
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
    $$;"""
    snowflake_utils.run_query(sf_connection, sp_sql)
