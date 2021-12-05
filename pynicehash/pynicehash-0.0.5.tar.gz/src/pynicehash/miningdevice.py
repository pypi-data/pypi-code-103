

class MiningDevice(object):
    def __init__(self, parent_rig, data):
        self.parent_rig = parent_rig
        self.id = data["id"]
        self.name = data["name"]
        self.device_type = data["deviceType"]["enumName"]
        self.status = data["status"]["enumName"]
        self.temperature = data["temperature"]
        self.load = data["load"]
        self.rpm = data["revolutionsPerMinute"]
        self.rpm_percentage = data["revolutionsPerMinutePercentage"]
        self.power_mode = data["powerMode"]["enumName"]
        self.power_usage = data["powerUsage"]
        self.intensity = data["intensity"]["enumName"]
