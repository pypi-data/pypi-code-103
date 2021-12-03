
from test_framework.dut.agent import Agent
from test_framework.dut.slot import Slot
from test_framework.database.dut_database import DutDatabase
from utils import log


class Dut(object):

    def __init__(self):
        self.agent = Agent()
        self.slot = Slot(self.agent)

    def refresh(self):
        log.INFO("Begin to refresh DUT")
        self.agent.refresh()
        self.slot.refresh()

    # def refresh_slots(self):
    #     slots = self.get_agent_slots()
    #     for slot in slots:
    #         slot_obj = Slot(slot[0], slot[1], slot[2])
    #         slot_obj.refresh()
