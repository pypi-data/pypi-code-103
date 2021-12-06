
import datetime
from resources.models.database import SqlConnection


class Cleaner(object):

    def __init__(self):
        self.sql = SqlConnection(db_name="performance_test")

    def get_all_tests(self):
        command_line = "SELECT * FROM _tests"
        tests = self.sql.execute_sql_command(command_line)
        return tests

    def filter_not_confirmed_finished_tests(self, tests):
        current_time = datetime.datetime.now()
        filter_tests = list()
        for test in tests:
            if test[15] == 0 and test[13] !=1:
                start_time = test[11]
                distance = current_time - start_time
                if distance.days > 15:
                    filter_tests.append(test)
        return filter_tests

    def delete_table(self, table):
        command_line = "DROP TABLE {}".format(table)
        self.sql.execute_and_commit_sql_command(command_line)

    def delete_row(self, index):
        command_line = "DELETE FROM _tests WHERE `index`={}".format(index)
        self.sql.execute_and_commit_sql_command(command_line)

    def delete_tests(self, tests):
        for test in tests:
            self.delete_table(test[6])
            self.delete_row(test[0])

    def get_tests(self, group_key):
        command_line = "SELECT * FROM _tests WHERE `group_key`='{}'".format(group_key)
        tests = self.sql.execute_sql_command(command_line)
        return tests

    def delete_test_group(self, group_key):
        tests = self.get_tests(group_key)
        self.delete_tests(tests)


if __name__ == '__main__':
    CL = Cleaner()
    CL.delete_test_group("20191024152701_bPHZGu8tCv")

