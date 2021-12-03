
from test_framework.database.dut_database import update_slot, check_lost_slot
from tool.device.linux_nvme import LinuxNvme
from test_framework.state import SlotState


class LinuxSlot(object):

    def __init__(self, db_slots, agent_name):
        self.db_slots = db_slots
        self.live_slots = list()
        self.agent_name = agent_name
        self.nvme = LinuxNvme()

    @update_slot
    def refresh(self, device):
        dev_info = self.nvme.get_info(int(device["ctrl_id"]))
        slot_info = self._format_results(dev_info, device)
        slot_id = self.get_slot_id(slot_info)
        print("refresh linux device", slot_id, slot_info)
        return slot_id, slot_info

    def get_slot_id(self, device):
        slot_id = -1
        for item in self.db_slots:
            if item[3] == device["slot"]:
                slot_id = item[0]
                self.live_slots.append(slot_id)
        return slot_id

    def refresh_all(self):
        devices = self.nvme.get_linux_nvme_devs()
        for item in devices:
            self.refresh(item)
        self.check_lost_slots()

    @check_lost_slot
    def is_slot_lost(self, slot):
        if slot[0] not in self.live_slots:
            return slot[0]
        else:
            return None

    def check_lost_slots(self):
        for item in self.db_slots:
            self.is_slot_lost(item)

    def _format_results(self, results, dev):
        format_result = {
            "slot": dev["name"],
            "vendor": results["ssd_config_dic"]["drive_pn"],
            "fw_version": results["test_fw_config_dic"]["fw_public_revision"],
            "commit": results["test_fw_config_dic"]["fw_private_revision"][0:6],
            "ise/sed": results["ssd_config_dic"]["security_type"],
            "sn": results["ssd_config_dic"]["drive_sn"],
            "cap": results["ssd_config_dic"]["drive_tnvmcap"],
            "bb": self.convert_t(results["drive_life_info_dic"]["count_grown_defects"]),
            "max_ec": results["drive_life_info_dic"]["nand_max_erase_count"],
            "avg_ec": results["drive_life_info_dic"]["nand_avg_erase_count"],
            "agent": self.agent_name,
            "status": SlotState.Idle
        }
        return format_result

    @staticmethod
    def convert_t(cap):
        return float('%.2f' % (cap/1000/1000/1000/1000))