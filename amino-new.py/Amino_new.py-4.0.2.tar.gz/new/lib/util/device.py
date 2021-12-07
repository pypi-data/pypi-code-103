import json
from .helpers import generate_device_info

class DeviceGenerator:
    def __init__(self, deviceId ="22088D0C471F6FFCC3D93B887BE782BA92733BB1573F6BEC436369F891CA6F9DF84CDFA287AEA0AAFE"):
        try:
            with open("device.json", "r") as stream:
                data = json.load(stream)
                self.user_agent = data["user_agent"]

                if deviceId:
                    self.device_id = deviceId
                else:
                    self.device_id = data["device_id"]

                self.device_id_sig = data["device_id_sig"]

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            device = generate_device_info()
            with open("device.json", "w") as stream:
                json.dump(device, stream, indent=4)

            with open("device.json", "r") as stream:
                data = json.load(stream)
                self.user_agent = data["user_agent"]

                if deviceId:
                    self.device_id = deviceId
                else:
                    self.device_id = data["device_id"]

                self.device_id_sig = data["device_id_sig"]
