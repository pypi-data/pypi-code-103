import re
import pathlib
from typing import Dict, Any, Optional
from .dupedict import DupeDict
from .syscalls import SysCommand
from .exceptions import ResourceNotFound, ResourceError

def DupeDict_to_qemu_string(struct :DupeDict) -> str:
	result = ''

	for key, val in struct:
		if type(val) == bool:
			result += f" -{key}"
		else:
			result += f" -{key} {val}"

	return result

def build_binary_start(namespace :Optional[str] = None) -> str:
	qemu_binary = 'qemu-system-x86_64'
	if namespace:
		qemu_binary = f'ip netns exec {namespace} {qemu_binary}'

	return qemu_binary

def handle_graphics(enable :bool = False) -> str:
	if not enable:
		return ' -display none -nographic'

	return ''

def handle_monitors(name :str) -> str:
	return f' -qmp unix:/tmp/{name}.qmp,server,nowait -monitor unix:/tmp/{name}.monitor,server,nowait'

def initialize_hardware(struct :DupeDict) -> str:
	return DupeDict_to_qemu_string(struct)

def build_pcie_buses(struct :DupeDict) -> str:
	return DupeDict_to_qemu_string(struct)

def build_pcie_root_ports(struct :DupeDict) -> str:
	return DupeDict_to_qemu_string(struct)

def build_pcie_slave_buses(struct :DupeDict) -> str:
	return DupeDict_to_qemu_string(struct)

def build_pcie_slave_devices(struct :DupeDict) -> str:
	return DupeDict_to_qemu_string(struct)

# https://hvornum.se/kvm_diagram.png
# https://news.ycombinator.com/item?id=19736722
# https://forums.freebsd.org/threads/qemu-kvm-and-shared-irq-for-dual-network-interfaces.78328/
def create_qemu_string(name :str, namespace :str, base_hardware :DupeDict, pcie_buses :DupeDict, pcie_root_ports :DupeDict, pcie_slave_buses :DupeDict, pcie_slave_devices :DupeDict, graphics :bool = False) -> str:
	qemu_string = build_binary_start(namespace)
	qemu_string += handle_graphics(graphics)
	qemu_string += handle_monitors(name)
	qemu_string += initialize_hardware(base_hardware)
	qemu_string += build_pcie_buses(pcie_buses)
	qemu_string += build_pcie_root_ports(pcie_root_ports)
	qemu_string += build_pcie_slave_buses(pcie_slave_buses)
	qemu_string += build_pcie_slave_devices(pcie_slave_devices)

	# print(qemu_string)
	return qemu_string

	# if dry-run: don't setup stuff

	# qemu_create_images(pcie_slave_devices)
	# write_service_file(name, qemu_string)

def verify_qemu_resources(name :str, namespace :str, base_hardware :DupeDict, pcie_buses :DupeDict, pcie_root_ports :DupeDict, pcie_slave_buses :DupeDict, pcie_slave_devices :DupeDict) -> bool:
	for device_type, value_string in pcie_slave_devices:
		if len(device_info_str := re.findall('file=.*?,|format=.*?,', value_string)) == 2:
			device_info_list = [x.split('=', 1) for x in device_info_str]
			device_info :Dict[Any, Any] = {}
			for item in device_info_list:
				device_info[item[0]] = item[1]
			
			if device_info.get('file'):
				device_location = pathlib.Path(device_info['file'].strip(', '))
				if not device_location.exists():
					if (device_format := device_info.get('format')) and device_format.startswith('qcow2'):
						raise ResourceNotFound(f"Could not locate qemu harddrive {device_location}")
					elif device_format and device_format.startswith('raw'):
						if 'media=cdrom' in value_string:
							raise ResourceNotFound(f"Could not locate qemu cdrom image {device_location}")
						else:
							raise ResourceNotFound(f"Could not locate qemu raw image {device_location}")
					else:
						raise ResourceNotFound(f"Could not locate qemu device resource {device_location}")
			else:
				raise ResourceError(f"No file definition for qemu resource {device_info}")

	return True


def qemu(cmd :str) -> SysCommand:
	return SysCommand(f"qemu {cmd}")

def qemu_img(cmd :str) -> SysCommand:
	return SysCommand(f"qemu-img {cmd}")

def write_qemu_service_file(location :pathlib.Path, name :str, namespace :str, qemu_config_path :pathlib.Path, qemu_string :str) -> bool:
	if location.exists():
		raise SystemError(f"Service file already exists: {location}")

	with location.open('w') as service:
		service.write(f'[Unit]\n')
		service.write(f'Description=Qemu instance of {name}\n')

		service.write(f"\n")
		service.write(f'[Service]\n')
		service.write(f"PIDFile=/run/ourkvm_{name}.pid\n")

		service.write(f"\n")
		service.write(f"ExecStartPre=/usr/bin/python -c 'import ourkvm; ourkvm.load_environment(\"{qemu_config_path}\")'\n")
		service.write(f'ExecStart={qemu_string}\n')

		service.write(f"\n")
		service.write(f"ExecStop=/usr/bin/python -m ourkvm --machine-name {name} --stop\n")
		service.write(f"ExecStopPost=/usr/bin/python -c 'import ourkvm; ourkvm.dismantle_environment(\"{qemu_config_path}\")'\n")
		# TODO: Monitor for changes to the environment?

		service.write(f"\n")
		service.write(f'[Install]\n')
		service.write(f'WantedBy=multi-user.target\n')

	return True