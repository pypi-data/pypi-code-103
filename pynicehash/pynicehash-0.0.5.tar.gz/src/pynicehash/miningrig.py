from pynicehash.miningdevice import MiningDevice

class MiningRig(object):
    def __init__(self, nicehash_api, data):
        self.nicehash_api = nicehash_api
        self.set_data(data)
    
    def set_data(self, data):
        self.id = data["rigId"]
        self.type = data["type"]
        self.name = data["name"]
        self.status_time = data["statusTime"]
        self.join_time = data["joinTime"]
        self.miner_status = data["minerStatus"]
        self.group_name = data["groupName"]
        self.unpaid_amount = data["unpaidAmount"]
        self.notification = data["notifications"]
        self.software_version = data["softwareVersions"]
        self.cpu_mining_enabled = data["cpuMiningEnabled"]
        self.cpu_exists = data["cpuExists"]
        self.profitability = data["profitability"]
        self.local_profitability = data["localProfitability"]
        self.rig_power_mode = data["rigPowerMode"]
        
        self.devices = []
        for d in data["devices"]:
            self.devices.append(MiningDevice(self, d))

    def update(self):
        self.set_data(self.nicehash_api.get_rig_detail(self.id))

    def set_device_status(self, device, mining_status):
        self.nicehash_api.set_device_status(device, mining_status)

