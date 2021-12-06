# pylint: disable=broad-except, invalid-name
import os
from resources.models.database import SqlConnection


class DutDatabase(SqlConnection):

    def __init__(self):
        super(DutDatabase, self).__init__(db_name="dutdb")
        self.agent_table = "agent"
        self.slot_table = "slot"

    def get_all_dut(self):
        agents = self._get_all_agent()
        for agent in agents:
            agent["slots"] = self._get_slots_by_agent(agent["name"])
        return agents

    def _get_all_agent(self):
        cmd = "SELECT * FROM {}".format(self.agent_table)
        agents = self.execute_sql_command(cmd)
        agents_dict = [self._convert_to_agent_dict(item) for item in agents]
        return agents_dict

    @staticmethod
    def _convert_to_agent_dict(agent_item):
        agent = {
            "id": agent_item[0],
            "name": agent_item[1],
            "os": agent_item[2],
            "ip": agent_item[3],
            "port": agent_item[4],
            "label": agent_item[5],
            "description": agent_item[6],
            "platform": agent_item[7],
            "update_time": agent_item[8],
            "status": agent_item[9]
        }
        return agent

    def _get_slots_by_agent(self, agent):
        cmd = "SELECT * FROM {} WHERE `agent`='{}'".format(self.slot_table, agent)
        slots = self.execute_sql_command(cmd)
        slots_dict = [self._convert_to_slot_dict(slot) for slot in slots]
        return slots_dict

    @staticmethod
    def _convert_to_slot_dict(slot_item):
        slot_dict = {
            "id": slot_item[0],
            "name": slot_item[1],
            "config_name": slot_item[2],
            "slot": slot_item[3],
            "vendor": slot_item[4],
            "fw_version": slot_item[5],
            "commit": slot_item[6],
            "ise/sed": slot_item[7],
            "sn": slot_item[8],
            "cap": slot_item[9],
            "bb": slot_item[10],
            "max_ec": slot_item[11],
            "status": slot_item[12],
            "update_time": slot_item[13]
        }
        return slot_dict

    def add_slot(self, slot_index, agent, config_name=""):
        self.insert_to_table(self.slot_table, name="slot_{}".format(slot_index), config_name=config_name, agent=agent)
        slot_id = self.get_slot_id()
        return slot_id

    def get_slot_id(self):
        cmd = "select max(id) from {}".format(self.slot_table)
        result = self.execute_sql_command(cmd)
        return result[0]

    def del_slot(self, slot_id):
        cmd = "delete from {} where `id`={}".format(self.slot_table, slot_id)
        self.cursor.execute(cmd)
        self.conn.commit()
