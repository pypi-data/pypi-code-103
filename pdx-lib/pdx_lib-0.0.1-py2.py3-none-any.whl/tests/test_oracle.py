from pdx import Config
from pdx import Session
from pdx import Console
from pdx.db import OracleConnection
from pdx.db import ConnectionHolder
from pdx.db import Query
from pdx.db import banner_service
from pdx import utility_service

import unittest

Session.debug_mode = True
out = Console.get()


class TestOracle(unittest.TestCase):
    """
    Test connecting to and querying Oracle
    """

    def test_connection(self):
        """
        Test connecting to Oracle
        """
        out.trace("test_connection")
        self.assertTrue(len(ConnectionHolder.connections) == 0, "There shouldn't be any existing connections")

        # Must be on PSU network (or VPN) to connect to the database
        if utility_service.is_on_psu_network():

            # Connect to database
            oracle = OracleConnection.OracleConnection(Config.default_sid)
            self.assertTrue(oracle is not None, "OracleConnection returned null")
            self.assertTrue(oracle.cx is not None, "CX for default sid is null")
            self.assertTrue(oracle.cx.version is not None, "No version information")

            # Connection should be held to prevent multiple connections
            self.assertTrue(len(ConnectionHolder.connections) == 1, "There should be 1 existing connection")

            oracle.close()

            # Closed connections should be forgotten
            self.assertTrue(oracle.cx is None, "Connection should be None")
            self.assertTrue(len(ConnectionHolder.connections) == 0, "Closed connection should have been forgotten")

            # Test multiple connections and connection re-use
            self.assertTrue(len(ConnectionHolder.connections) == 0, "There shouldn't be  existing connections (MULTI)")
            default_sid = OracleConnection.OracleConnection(Config.default_sid)
            self.assertTrue(len(ConnectionHolder.connections) == 1, "There should be 1 existing connection (MULTI)")
            alternate_sid = OracleConnection.OracleConnection(Config.alternate_sid)
            self.assertTrue(len(ConnectionHolder.connections) == 2, "There should be 2 existing connections (MULTI)")
            default_sid_2 = OracleConnection.OracleConnection(Config.default_sid)
            self.assertTrue(len(ConnectionHolder.connections) == 2, "There should still be 2 connections (MULTI)")

            default_sid_2.close()
            self.assertTrue(len(ConnectionHolder.connections) == 1, "There should be 1 connection left (MULTI)")
            alternate_sid.close()
            self.assertTrue(len(ConnectionHolder.connections) == 0, "There should be no connections left (MULTI)")

            self.assertFalse(default_sid_2.is_active(), "SID2 should be inactive (MULTI)")
            self.assertFalse(default_sid.is_active(), "SID should be inactive because SID2 was closed (MULTI)")

            ConnectionHolder.closeout()
            self.assertTrue(len(ConnectionHolder.connections) == 0, "There shouldn't be any remaining connections")

        else:
            print("Skipping Oracle tests because you're not on the PSU network.")

    def test_query(self):
        """
        Test the Query class
        """
        out.trace("test_query")
        self.assertTrue(len(ConnectionHolder.connections) == 0, "There shouldn't be any existing connections")

        # Must be on PSU network (or VPN) to connect to the database
        if utility_service.is_on_psu_network():
            # Query Value
            query = Query.Query(Config.default_sid, "select user from dual")
            self.assertTrue(query.value() == Session.username.upper(), "Could not select user")
            query = Query.Query(Config.default_sid, "select user, 'x' from dual")
            self.assertTrue(query.value() == Session.username.upper(), "Could not select value from 2-column query")
            del query

            # Test connection re-use
            self.assertTrue(len(ConnectionHolder.connections) == 1, "There should only be one existing connection")

            # Test a list of result maps
            query = Query.Query(Config.default_sid, "select * from nbrbjob where nbrbjob_pidm = :1;", [1049650])
            results = query.results()
            self.assertTrue(len(results) > 2, "There should be multiple results")
            self.assertTrue(results[0]['NBRBJOB_POSN'].startswith('D'), "Reference by column name failed")

            # Close all connections
            ConnectionHolder.closeout()
            self.assertTrue(len(ConnectionHolder.connections) == 0, "There shouldn't be any remaining connections")

    def test_finding_database_objects(self):
        """
        Test identifying database objects in a block of text
        """
        out.trace("test_finding_database_objects")

        text = """
        
    /** getLatestAdmitTerm
     *
     * Get the latest admit term for given user/level/GradTerm
     *
     * Parameters:
     *      1. Student pidm
     *************************************************************************/
    @Transactional(readOnly = true)
    String getLatestAdmitTerm(def pidm, String level, String gradTermCode) {
        messageService?.trace('getLatestAdmitTerm', [pidm, level, gradTermCode], "debug")
        try{
            Sql sql = connectionService.getBannerConnection()

            def result = sql.firstRow(\"""
                SELECT MAX(sarappd_term_code_entry) as term_code
                  FROM sarappd A, spriden
                 WHERE spriden_pidm = ${pidm}
                   AND spriden_change_ind is null
                   AND spriden_pidm = A.sarappd_pidm
                   AND (A.SARAPPD_APDC_CODE = 'T1' or a.sarappd_apdc_code like 'A%')
                   AND A.sarappd_appl_no = (
                        SELECT max(saradap_appl_no)
                          FROM saradap
                         WHERE saradap_pidm = sarappd_pidm
                           AND saradap_apst_code = 'D'
                           AND saradap_levl_code = ${level}
                           AND saradap_term_code_entry = sarappd_term_code_entry
                   )
                   AND sarappd_seq_no = (
                        SELECT max(b.sarappd_seq_no)
                          FROM sarappd b
                         WHERE b.sarappd_pidm = A.sarappd_pidm
                           AND b.sarappd_appl_no = A.sarappd_appl_no
                           AND b.sarappd_term_code_entry = A.sarappd_term_code_entry
                           AND B.sarappd_apdc_code != 'X'
                   )
                   AND sarappd_term_code_entry <= ${gradTermCode}
            \""")
            return result?.term_code
        }
        catch(ee){
            messageService?.unexpectedError(ee, "Could not get latest admit term")
            return null
        }
    }

    /** getWebTailorParameter()
     *
     *  Get a parameter from WebTailor
     *
     *  Returns: <String> parameter value
     *
     *************************************************************************/
    @Transactional(readOnly = true)
    String getWebTailorParameter(String paramName) {
        messageService?.trace('getWebTailorParameter', [paramName], "debug")
        try{
            Sql sql = connectionService.getBannerConnection()
            return sql.firstRow(\"""
                   SELECT twgbparm_param_value as value
                     FROM twgbparm
                    WHERE twgbparm_param_name = ${paramName}
            \""")?.value
        }
        catch(ee){
            messageService?.unexpectedError(ee, "Could not get WebTailor parameter")
            return null
        }
    }


    /** getZgvsdax()
     *
     *  Get a results from ZGVSDAX
     *
     *  Returns: <List> Groovy SQL results
     *
     *************************************************************************/
    @Transactional(readOnly = true)
    List<Zgvsdax> getZgvsdax(String group='%', String item='%', sequence='%') {
        messageService?.trace("getZgvsdax", [group, item, sequence], 'debug')
        List<Zgvsdax> resultList = []
        try{
            Sql sql = connectionService.getBannerConnection()
            sql.rows(\"""
               SELECT zgvsdax_group, zgvsdax_item, zgvsdax_seqno,
                      anydata.AccessVarchar2(zgvsdax_value) as zgvsdax_value,
                      zgvsdax_desc,
                      zgvsdax_activity_date,
                      zgvsdax_user_id
                 FROM zgvsdax
                WHERE zgvsdax_group LIKE ${group}
                  AND zgvsdax_item LIKE ${item}
                  AND zgvsdax_seqno LIKE ${sequence}
             ORDER BY zgvsdax_group, zgvsdax_item, zgvsdax_seqno
            \""")?.each{ GroovyRowResult row ->
                resultList << new Zgvsdax(row)
            }
            sql.execute(\"""
                DELETE FROM zgvsdax WHERE 'yes' = 'no'
            \""")
            sql.execute(\"""
                Update zgvsdax
                 set zgvsdax_item = 100
                 WHERE 'yes' = 'no'
            \""")
        }
        catch(ee){
            messageService?.unexpectedError(ee, "Could not get ZGVSDAX values")
        }
        return resultList
    }
        """

        # Look for database objects in the above text
        results = banner_service.find_queryable_objects(text, Config.default_sid)
        # Close connections and clear cached data
        ConnectionHolder.closeout()

        # Test the results
        self.assertTrue(len(results) == 5, "There should be 5 queryable objects in the text")
        self.assertTrue('DELETE' in results['ZGVSDAX']['privileges'], "ZGVSDAX: Missing DELETE")
        self.assertTrue('UPDATE' in results['ZGVSDAX']['privileges'], "ZGVSDAX: Missing UPDATE")
        self.assertTrue('SELECT' in results['ZGVSDAX']['privileges'], "ZGVSDAX: Missing SELECT")


if __name__ == '__main__':
    unittest.main()
    ConnectionHolder.closeout()
    Console.goodbye(print_log_path=True)
