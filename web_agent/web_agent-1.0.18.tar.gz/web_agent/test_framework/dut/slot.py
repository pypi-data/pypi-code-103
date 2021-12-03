
from test_framework.dut.sub_slot.oakgate_slot import OakgateSlot
from test_framework.dut.sub_slot.linux_slot import LinuxSlot
from test_framework.database.dut_database import DutDatabase
from utils.system import get_platform


class Slot(object):

    def __init__(self, agent):
        self.agent = agent
        self.agent_name = self.agent.get_agent_name()
        self.db_client = DutDatabase()
        self.platform = get_platform()

    def refresh(self):
        slots = self.db_client.get_agent_related_slots(self.agent_name)
        if self.platform == "oakgate":
            self.oakgate_refresh(slots)
        else:
            self.linux_refresh(slots)

    def oakgate_refresh(self, slots):
        oak_slot = OakgateSlot(slots, self.agent_name)
        oak_slot.refresh_all()

    def linux_refresh(self, slots):
        slot = LinuxSlot(slots, self.agent_name)
        slot.refresh_all()
