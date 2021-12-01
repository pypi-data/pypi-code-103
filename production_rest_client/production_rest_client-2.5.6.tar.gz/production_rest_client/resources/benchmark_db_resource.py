# coding=utf-8
# pylint: disable=import-error, broad-except
from resources.models.database import SqlConnection
from resources.delete_old_data import Cleaner

class BenchmarkDBResource(object):

    def __init__(self, db_name="performance_test"):
        self.sql = SqlConnection(db_name=db_name)
        self.cleaner = Cleaner()

    def __del__(self):
        del self.sql

    def _get_search_match_string(self, test_key=None, project_name=None, begin_time=None, end_time=None, test_name=None):
        search_str = "SELECT * FROM _tests"
        is_first_filter = True
        if project_name is not None:
            match_string = self._get_project_name_match_string(project_name)
            search_str = self._generate_filter_string(search_str, match_string, is_first_filter)
            is_first_filter = False
        if begin_time is not None and end_time is not None:
            match_string = self._get_search_date_match_string(begin_time, end_time)
            search_str = self._generate_filter_string(search_str, match_string, is_first_filter)
            is_first_filter = False
        if test_name is not None:
            match_string = self._get_test_name_match_string(test_name)
            search_str = self._generate_filter_string(search_str, match_string, is_first_filter)
        if test_key is not None:
            match_string = self._get_test_key_match_string(test_key)
            search_str = self._generate_filter_string(search_str, match_string, is_first_filter)
        return search_str

    def delete_test_group(self, group_key):
        return self.cleaner.delete_test_group(group_key)

    @staticmethod
    def _get_test_key_match_string(test_key):
        match_str = "`group_key`='{}'".format(test_key)
        return match_str

    @staticmethod
    def _get_project_name_match_string(project_name):
        match_str = "project_name like '%{}%'".format(project_name)
        return match_str

    @staticmethod
    def _get_search_date_match_string(begin_time, end_time):
        match_string = "DATE_FORMAT(start_time,'%Y%m%d') BETWEEN '{}' and '{}'".format(begin_time, end_time)
        return match_string

    @staticmethod
    def _get_test_name_match_string(test_name):
        match_str = "group_name like '%{}%'".format(test_name)
        return match_str

    @staticmethod
    def _generate_filter_string(base_string, new_filter, is_first_filter):
        if is_first_filter:
            base_string = "{} WHERE ".format(base_string)
        else:
            base_string = "{} AND ".format(base_string)
        search_string = "{} {}".format(base_string, new_filter)
        return search_string

    def _get_spec_index(self, main_index, get_index_name):
        command = "SELECT `{}` FROM _tests WHERE `index`={}".format(get_index_name, main_index)
        self.sql.cursor.execute(command)
        tests = self.sql.cursor.fetchall()
        env_index = tests[0][0] if tests else None
        return env_index

    def _get_real_time_results(self, test_index, real_timi_mini_index=None):
        real_time_table_name = self._get_spec_index(test_index, "real_time_index")
        if real_timi_mini_index is None:
            command = "SELECT * FROM {}".format(real_time_table_name)
        else:
            command = "SELECT * FROM {} WHERE `index`>{}".format(real_time_table_name, real_timi_mini_index)
        results = self.sql.execute_sql_command(command)
        results_dict = [{"index":item[0], "time":item[6], "read_iops": item[1], "read_bw":item[2], "write_iops":item[3],
                         "write_bw":item[4], "temperature": item[5]} for item in results]
        return results_dict

    # def execute_sql_command(self, command):
    #     results = list()
    #     try:
    #         self.sql.cursor.execute(command)
    #         results = self.sql.cursor.fetchall()
    #     except BaseException as message:
    #         print(message)
    #     return results

    def _get_test_config(self, index):
        results_dict = dict()
        config_index = self._get_spec_index(index, "config_index")
        command = "SELECT * FROM _configuration WHERE `index`={}".format(config_index)
        results = self.sql.execute_sql_command(command)
        if results:
            results_dict = {
                "type": results[0][1],
                "ioengine": results[0][3],
                "blocksize": results[0][4],
                "iodepth": results[0][5],
                "numjobs": results[0][6],
                "rw": results[0][7],
                "rwmixread": results[0][8],
                "size": results[0][9],
                "runtime": results[0][10],
            }
        return results_dict

    def _get_env_by_index(self, index):
        results_dict = dict()
        env_index = self._get_spec_index(index, "test_env_index")
        command = "SELECT * FROM _environment WHERE `index`={}".format(env_index)
        results = self.sql.execute_sql_command(command)
        if results:
            results_dict = {
                "vendor": results[0][1],
                "vendor_name": results[0][2],
                "operating_system": results[0][3],
                "ip": results[0][4],
                "capacity": results[0][5],
                "device": results[0][8],
                "fw_version": results[0][9]
            }
        return results_dict

    def _get_summary_report_by_index(self, index):
        result_dict = dict()
        report_index = self._get_spec_index(index, "summary_report_index")
        command = "SELECT * FROM _summary_test_results WHERE `index`={}".format(report_index)
        results = self.sql.execute_sql_command(command)
        if results:
            result_dict = {"iops_read":results[0][1],
                           "bw_read":results[0][2],
                           "io_read":results[0][3],
                           "avg_latency_read":results[0][4],
                           "max_latency_read": results[0][22],
                           "min_latency_read": results[0][23],
                           "percent_99_read": results[0][26],
                           "percent_999_read": results[0][5],
                           "percent_9999_read": results[0][6],
                           "percent_99999_read": results[0][7],
                           "percent_999999_read": results[0][8],
                           "percent_9999999_read": results[0][9],
                           "percent_99999999_read": results[0][10],
                           "iops_write": results[0][11],
                           "bw_write": results[0][12],
                           "io_write": results[0][13],
                           "avg_latency_write": results[0][14],
                           "max_latency_write": results[0][24],
                           "min_latency_write": results[0][25],
                           "percent_99_write": results[0][27],
                           "percent_999_write": results[0][15],
                           "percent_9999_write": results[0][16],
                           "percent_99999_write": results[0][17],
                           "percent_999999_write": results[0][18],
                           "percent_9999999_write": results[0][19],
                           "percent_99999999_write": results[0][20]}
        return result_dict

    @staticmethod
    def _get_duration(start_time, end_time):
        duration = 0
        if start_time is not None and end_time is not None:
            duration = end_time - start_time
        return duration

    def _get_test_state_by_index(self, index):
        result = None
        command = "SELECT state FROM _tests WHERE `index`={}".format(index)
        results = self.sql.execute_sql_command(command)
        if results:
            result = results[0][0]
        return result

    def _search_tests_by_group_key(self, group_key):
        sea_string = "SELECT * FROM _tests WHERE group_key='{}'".format(group_key)
        result = self.sql.execute_sql_command(sea_string)
        return result

    def _search_test_name(self, test_name):
        sea_string = "SELECT * FROM _tests WHERE group_name='{}'".format(test_name)
        result = self.sql.execute_sql_command(sea_string)
        return result

    def _search_step_by_key(self, step_key):
        sea_string = "SELECT * FROM _tests WHERE `key`='{}'".format(step_key)
        result = self.sql.execute_sql_command(sea_string)
        return result
    
    def get_index_by_key(self, key):
        result = None
        command = "SELECT `index` FROM _tests WHERE `key`='{}'".format(key)
        results = self.sql.execute_sql_command(command)
        if results:
            result = results[0][0]
        return result

    def confirm_test(self, step_key):
        """

        :param step_key:
        :return:
        """
        cmd = "UPDATE _tests SET confirmed=1 where `key`='{}'".format(step_key)
        self.sql.cursor.execute(cmd)
        self.sql.conn.commit()

    def confirm_group(self, group_key):
        """
        confirm whole group tests
        :param group_key:
        :return:
        """
        cmd = "UPDATE _tests SET confirmed=1 where `group_key`='{}'".format(group_key)
        self.sql.cursor.execute(cmd)
        self.sql.conn.commit()

    def check_test_name(self, test_name):
        """
        check test is exit
        :param test_name:
        :return:
        """
        ret = self._search_test_name(test_name)
        return ret

    def search(self, test_key=None, project_name=None, begin_time=None, end_time=None, test_name=None):
        """
        :param project_name: project name, like tahoe, alpha
        :param begin_time: format: '%Y%m%d', e.g. 20170601
        :param end_time: format: '%Y%m%d', e.g. 201901101
        :param test_name:
        :param test_key:
        :return:
        """
        test_results = list()
        if test_key is None:
            search_str = self._get_search_match_string(test_key, project_name, begin_time, end_time, test_name)
            results = self.sql.execute_sql_command(search_str)
            group_key_list = [item[4] for item in results if item[4] is not None]
            group_key_list = list(set(group_key_list))
        else:
            group_key_list = test_key
        for group_key in group_key_list:
            results = self._search_tests_by_group_key(group_key)
            test = {
                "name": results[0][2],
                "project_name": results[0][3].upper(),
                "start_time": results[0][11],
                "end_time": results[0][12],
                "tester": results[0][14],
                "test_key": group_key,
                "environment": self._get_env_by_index(results[0][0]),
                "confirm": results[0][15]
            }
            test_results.append(test)
        return test_results

    def get_test_detail_information(self, test_key):
        """
        get test detail information by test key
        :param test_key:
        :return:
        """
        results = self._search_tests_by_group_key(test_key)
        test_steps = list()
        for item in results:
            step = {
                "index":item[0],
                "name":item[1],
                "group_name": item[2],
                "key":item[10],
                "start_time":item[11],
                "end_time":item[12],
                "state":item[13],
                "duration": self._get_duration(item[11], item[12]),
                "environment": self._get_env_by_index(item[0]),
                "summary_report": self._get_summary_report_by_index(item[0]),
                "configuration": self._get_test_config(item[0])}
            test_steps.append(step)
        return test_steps

    def get_step_detail_information(self, step_key):
        """
        get step detail information
        :param step_key:
        :return:
        """
        step = None
        result = self._search_step_by_key(step_key)
        if result:
            result = result[0]
            step = {
                "index":result[0],
                "name":result[1],
                "group_name": result[2],
                "key":result[10],
                "start_time":result[11],
                "end_time":result[12],
                "state":result[13],
                "duration":self._get_duration(result[11], result[12]),
                "environment": self._get_env_by_index(result[0]),
                "summary_report": self._get_summary_report_by_index(result[0]),
                "configuration": self._get_test_config(result[0])}
        return step

    def get_real_time_results(self, key, mini_index=None):
        """

        :param key: the test which want to get the real time
        :param mini_index: get the real time data index more then the mini_index
        :return:
        """
        index = self.get_index_by_key(key)
        result = self._get_real_time_results(index, mini_index)
        return result

    def get_test_state(self, key):
        """
        get test state by test key
        :param key:
        :return:
        """
        index = self.get_index_by_key(key)
        return self._get_test_state_by_index(index)

    def get_project_names(self):
        sea_string = "SELECT project_name FROM project_name "
        result = self.sql.execute_sql_command(sea_string)
        return result

    def add_project_name(self, new_name):
        insert_command = "INSERT INTO  project_name (project_name) VALUES ('{}')".format(new_name)
        print(insert_command)
        self.sql.execute_and_commit_sql_command(insert_command)
