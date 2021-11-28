from dataclasses import dataclass

from sleepstudyparser.constants.ModernStandbyType import ModernStandbyType


@dataclass
class Drips:
    sw_drips: int
    hw_drips: int
    modern_standby_type: ModernStandbyType

    @classmethod
    def make(cls, data, duration_in_seconds):
        sw_drips, hw_drips, connected_or_disconnected = 0, 0, 0
        if values := data.get("Values"):
            for value in values:
                key = value.get("Key")
                key_value = value.get("Value")
                if key == "Info.SwLowPowerStateTime":
                    sw_drips = 100 * key_value / (duration_in_seconds * 1000000) / 10
                if key == "Info.HwLowPowerStateTime":
                    hw_drips = 100 * key_value / (duration_in_seconds * 1000000) / 10
                if key == "Settings.ConnectedStandby":
                    connected_or_disconnected = int(key_value)
        return cls(
            sw_drips=int(round(sw_drips)),
            hw_drips=int(round(hw_drips)),
            modern_standby_type=ModernStandbyType(connected_or_disconnected),
        )

    def __str__(self):
        return (
            f"\nSW Drips: {self.sw_drips}%"
            f"\tHW Drips: {self.hw_drips}%"
            f"\tType: {self.modern_standby_type.name}"
        )
