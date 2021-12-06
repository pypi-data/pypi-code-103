# coding=utf-8
# pylint: disable=import-error, broad-except
from resources.models.database import SqlConnection


class EnvDBResource(object):

    def __init__(self, db_name="nodes"):
        self.sql = SqlConnection(db_name=db_name)

    def __del__(self):
        del self.sql

    def _get_all_nodes(self):
        sea_string = "SELECT * FROM node"
        result = self.sql.execute_sql_command(sea_string)
        return result

    def _get_node(self, ip, port=5000):
        table_name = self.get_node_table_name(ip, port)
        if table_name is not None:
            sea_string = "SELECT * FROM `{}`".format(table_name)
            result = self.sql.execute_sql_command(sea_string)
        else:
            result = list()
        return result

    def get_node_table_name(self, ip, port):
        sea_string = "SELECT state_table FROM node WHERE `ip`='{}' AND `port`={}".format(ip, port)
        table_name = self.sql.execute_sql_command(sea_string)
        table_name = table_name[0][0] if table_name else None
        return table_name

    @staticmethod
    def _sort_records_by_date(records):
        records_dict = dict()
        for item in records:
            record_time = item[2]
            record_date = record_time.date()
            record_date_str = record_date.strftime('%D')
            if record_date_str in records_dict.keys():
                records_dict[record_date_str].append(item)
            else:
                records_dict[record_date_str] = [item]
        return records_dict

    @staticmethod
    def statistics_daily_usage(records_sorted):
        work_time_dict = list()
        for key,value in  records_sorted.items():
            start_time = None
            work_time_list = list()
            for item in value:
                if item[1] == "running":
                    if start_time is None:
                        start_time = item[2]
                    else:
                        temp_work_time = item[2] - start_time
                        work_time_list.append(temp_work_time.total_seconds())
                        start_time = item[2]
                elif item[1] == "idle" and start_time is not None:
                    temp_work_time = item[2] - start_time
                    work_time_list.append(temp_work_time.total_seconds())
                    start_time = None
                elif item[1] == "online":
                    start_time = None
            result = {
                "date": key,
                "usage":float('%.4f'% (sum(work_time_list)/86400)),
                "total_time":sum(work_time_list)
            }
            if result["total_time"] > 0:
                work_time_dict.append(result)
        return work_time_dict

    def get_nodes(self):
        """
        get all node information
        :return:
        """
        node_list = list()
        nodes = self._get_all_nodes()
        for node in nodes:
            node_item = {
                "index":node[0],
                "name":node[6],
                "ip":node[1],
                "project":node[8],
                "vendor":node[9],
                "fw":node[10],
                "state":node[4],
                "system":node[3],
                "description":node[7],
                "port": node[14],
                "update_time": node[15],
                "platform": node[13]
            }
            node_list.append(node_item)
        return node_list

    def get_node_usage_rate(self, ip, port=5000):
        """
        get one node usage rate and running time by ip address
        :param ip:
        :return:
        """
        records = self._get_node(ip, port)
        records_dict = self._sort_records_by_date(records)
        work_time_dict = self.statistics_daily_usage(records_dict)
        return work_time_dict

    def set_project_name(self, ip, project_name):
        """
        set project name to node
        :param ip:
        :param project_name:
        :return:
        """
        cmd = "UPDATE node SET project='{}' where `ip`='{}'".format(project_name, ip)
        self.sql.cursor.execute(cmd)
        self.sql.conn.commit()
