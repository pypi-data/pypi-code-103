import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
from rest_client import RestClient
from db_client import DBClient


class Api(object):

    def __init__(self):
        self.db_client = DBClient()

    def __del__(self):
        del self.db_client

    def get_node_info(self, ip=None, port=5000):
        """
        get node information, if ip is None, will get all node information
        :param ip:
        :return: node information list
        """
        node_list = self.db_client.env_resource.get_nodes()
        if ip is not None:
            node_list = [node for node in node_list if (node["ip"] == ip and node["port"] == port)]
        for index, item in enumerate(node_list):
            rest_client = RestClient(item["ip"], port)
            ret = rest_client.state.get_state()
            node_list[index]["state"] = ret["data"][0] if ret["state"] == 1 else "offline"
            node_list[index]["automation"] = ret["data"][4] if ret["state"] == 1 else "None"
        return node_list

    def set_project_name(self, node_ip, project_name):
        """
        set node project name
        :param ip:
        :param project_name:
        :return:
        """
        self.db_client.env_resource.set_project_name(node_ip, project_name)

    def get_tests_detail(self, ip, port=5000, numbers=10):
        """
        get tests of node
        :param ip: node ip address
        :param numbers: numbers of tests want to return
        :return:tests information
        """
        tests = self.db_client.test_resource.get_tests_by_ip(ip, port, numbers)
        return tests

    def get_node_usage(self, ip, port=5000):
        """
        get one node usage rate and running time by ip address
        :param ip:
        :return:
        """
        node_usage = self.db_client.env_resource.get_node_usage_rate(ip, port)
        return node_usage

    def search(self, project_name=None, begin_time=None, end_time=None, test_name=None):
        """
        :param project_name: project name, like tahoe, alpha
        :param begin_time: format: '%Y%m%d', e.g. 20170601
        :param end_time: format: '%Y%m%d', e.g. 201901101
        :param test_name:
        :param test_key:
        :return:
        """
        return self.db_client.benchmark_resource.search(project_name, begin_time, end_time, test_name)

    def get_test_detail_information(self, test_key):
        return self.db_client.benchmark_resource.get_test_detail_information(test_key)

    def get_step_detail_information(self, step_key):
        return self.db_client.benchmark_resource.get_step_detail_information(step_key)

    def get_real_time_results(self, key, mini_index=None):
        return self.db_client.benchmark_resource.get_real_time_results(key, mini_index)

    def get_test_state(self, key):
        return self.db_client.benchmark_resource.get_test_state(key)

    def delete_performance_result(self, group_key):
        return self.db_client.benchmark_resource.delete_test_group(group_key)

    def add_project_name(self, project_name):
        return self.db_client.benchmark_resource.add_project_name(project_name)

    def get_project_names(self):
        rets = self.db_client.benchmark_resource.get_project_names()
        project_names = [item[0] for item in rets]
        return project_names
