
import os
import platform
from utils.system import get_ip_address, get_platform
from test_framework.database.dut_database import update_agent


class Agent(object):

    def __init__(self):
        self.ip_address = get_ip_address()
        self.port = os.environ.get('agent_port', '5000')

    def get_agent_info(self):
        agent_info = dict()
        agent_info["ip"] = self.ip_address
        agent_info["port"] = self.port
        agent_info["os"] = "windows" if platform.system() == 'Windows' else "linux"
        agent_info["platform"] = get_platform()
        return agent_info

    def get_agent_name(self):
        return "{}:{}".format(self.ip_address, self.port)

    @update_agent
    def refresh(self):
        return self.get_agent_info()


if __name__ == '__main__':
    ag = Agent()
    ag.refresh()
