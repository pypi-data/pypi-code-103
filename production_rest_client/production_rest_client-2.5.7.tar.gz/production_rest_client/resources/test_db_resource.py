# coding=utf-8
# pylint: disable=import-error, broad-except
from resources.models.database import SqlConnection


class TestDBResource(object):

    def __init__(self, db_name="production_test"):
        self.sql = SqlConnection(db_name=db_name)

    def __del__(self):
        del self.sql

    def get_result(self, key):
        cmd = "SELECT * FROM test_results WHERE test_key='{}'".format(key)
        self.sql.cursor.execute(cmd)
        result = self.sql.cursor.fetchone()
        if result is not None:
            result = list(result)
            if result[7] is not None:
                log = result[7][-10000:]   # reduce log size : Liangmin requirement
                result[7] = log
            else:
                result[7] = ""
        return result

    def get_latest_tests_from_db(self, ip, port, numbers):
        cmd = "SELECT * FROM test_results WHERE ip='{}' AND portORDER BY `index` DESC  LIMIT {}".format(ip, numbers)
        self.sql.cursor.execute(cmd)
        results = self.sql.cursor.fetchall()
        return results

    def get_tests_by_ip(self, ip, port=5000, numbers=10):
        tests = list()
        results = self.get_latest_tests_from_db(ip, port, numbers)
        for item in results:
            duration = (item[9]-item[8]).total_seconds() if None not in [item[8],item[9]] else 0
            log = item[7]
            if (log is not None) and (type(log)==str):
                log = log[-10000:]
            test = {
                "name": item[2],
                "state": item[4],
                "start_time": item[8],
                "end_time": item[9],
                "duration": duration,
                "log": log}
            tests.append(test)
        return tests


if __name__ == '__main__':
    DB = TestDBResource()
    tests1 = DB.get_result("9cd1r0nbc2")
    pass
