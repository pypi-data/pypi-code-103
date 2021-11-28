from .cpu_mon import CpuMonitor
from .disk_mon import DiskMonitor
from .mem_mon import MemoryMonitor
from .network_mon import NetworkMonitor
from .overview import MachineData


class AgentReport:
    agent_version = None
    MachineData = None
    Storage = None
    Network = None
    Memory = None
    Cpu = None

    def __init__(self, agent_report):
        self.agent_version = agent_report.get('agent', {}).get('version')
        self.overview = MachineData(agent_report.get('overview', {}))
        self.Storage = DiskMonitor(
            disk_mon_data=agent_report.get('plugins', {}).get('disk_mon', {}),
            cloud_vendor=agent_report.get('overview', {}).get('cloud', 'Amazon')
        )
        self.Memory = MemoryMonitor(agent_report.get('plugins', {}).get('mem_mon', {}))
        self.Cpu = CpuMonitor(agent_report.get('plugins', {}).get('cpu_mon', {}))
        self.Network = NetworkMonitor(agent_report.get('plugins', {}).get('network_mon', {}))