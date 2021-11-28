import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from sleepstudyparser.objects.State import State


@dataclass
class Report:
    computer_name: str
    system_manufacturer: str
    system_product_name: str
    bios_date: str
    bios_version: str
    connected_standby: bool
    platform_role: str
    os_build: str
    states: List[State]

    @classmethod
    def make(cls, file):
        text = Path(file).read_text()
        start_string = "var LocalSprData = "
        start = text.find(start_string)
        end = text.find(";\n\n", start)
        if start == -1 or end == -1:
            return None
        spr_data = text[start + len(start_string): end].replace("0x0", "0")
        json_data = json.loads(spr_data or "{}")
        computer_name = json_data.get("SystemInformation").get("ComputerName")
        system_manufacturer = json_data.get("SystemInformation").get(
            "SystemManufacturer"
        )
        system_product_name = json_data.get("SystemInformation").get(
            "SystemProductName"
        )
        bios_date = json_data.get("SystemInformation").get("BIOSDate")
        bios_version = json_data.get("SystemInformation").get("BIOSVersion")
        connected_standby = json_data.get("SystemInformation").get("ConnectedStandby")
        platform_role = json_data.get("SystemInformation").get("PlatformRole")
        os_build = json_data.get("SystemInformation").get("OSBuild")
        scenario_instances = json_data.get("ScenarioInstances", list())

        states = list()

        for scenario_instance in scenario_instances:
            states.append(State.make(scenario_instance))

        return cls(
            computer_name=computer_name,
            system_manufacturer=system_manufacturer,
            system_product_name=system_product_name,
            bios_date=bios_date,
            bios_version=bios_version,
            connected_standby=connected_standby,
            platform_role=platform_role,
            os_build=os_build,
            states=states,
        )

    def __str__(self):
        states_str = "\n".join([str(state) for state in self.states])
        return (
            f"\nCOMPUTER NAME: {self.computer_name}"
            f"\nSYSTEM PRODUCT NAME: {self.system_manufacturer} "
            f"{self.system_product_name}"
            f"\nBIOS: {self.bios_version} {self.bios_date}"
            f"\nOS BUILD: {self.os_build}"
            f"\nMODERN STANDBY ENABLED: {self.connected_standby}"
            f"\nPLATFORM ROLE: {self.platform_role}"
            f"\n\nSTATES:\n{states_str}"
        )
