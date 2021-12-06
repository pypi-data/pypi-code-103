import json
import socket
import psutil
import sys
from typing import Dict, List, Any, Optional, Union, Iterator

from ..syscalls import SysCommand
from ..exceptions import NamespaceNotFound, NamespaceError, UnsupportedHardware, InterfaceNotFound, InterfaceError

if sys.platform == 'linux':
	from select import epoll as epoll
	from select import EPOLLIN as EPOLLIN
	from select import EPOLLHUP as EPOLLHUP
else:
	import select
	EPOLLIN = 0
	EPOLLHUP = 0

	class epoll():
		""" #!if windows
		Create a epoll() implementation that simulates the epoll() behavior.
		This so that the rest of the code doesn't need to worry weither we're using select() or epoll().
		"""
		def __init__(self) -> None:
			self.sockets: Dict[str, Any] = {}
			self.monitoring: Dict[int, Any] = {}

		def unregister(self, fileno :int, *args :List[Any], **kwargs :Dict[str, Any]) -> None:
			try:
				del(self.monitoring[fileno])
			except:
				pass

		def register(self, fileno :int, *args :int, **kwargs :Dict[str, Any]) -> None:
			self.monitoring[fileno] = True

		def poll(self, timeout: float = 0.05, *args :str, **kwargs :Dict[str, Any]) -> List[Any]:
			try:
				return [[fileno, 1] for fileno in select.select(list(self.monitoring.keys()), [], [], timeout)[0]]
			except OSError:
				return []

class ip:
	@staticmethod
	def link(*args :str) -> SysCommand:
		return SysCommand(f"ip link {' '.join(args)}")

	@staticmethod
	def netns(*args :str) -> SysCommand:
		return SysCommand(f"ip netns {' '.join(args)}")

	@staticmethod
	def tuntap(*args :str) -> SysCommand:
		return SysCommand(f"ip tuntap {' '.join(args)}")

def add_namespace(namespace :str) -> bool:
	return bool(ip.netns(f"add {namespace}").exit_code == 0)

def del_namespace(namespace :str) -> bool:
	return bool(ip.netns(f"del {namespace}").exit_code == 0)

def run_namespace(namespace :str, *args :str) -> bool:
	return bool(ip.netns(f"exec {namespace}", *args).exit_code == 0)

def add_bridge(ifname :str, namespace :Optional[str] = None) -> bool:
	if namespace:
		if ip.netns(f"exec {namespace} ip link add name {ifname} type bridge").exit_code == 0:
			return bool(ip.netns(f"exec {namespace} ip link set dev {ifname} up").exit_code == 0)
	else:
		if ip.link(f"add name {ifname} type bridge").exit_code == 0:
			return bool(ip.link(f"set dev {ifname} up").exit_code == 0)
	return False

def add_if_to_bridge(bridge :str, ifname :str, namespace :Optional[str] = None) -> bool:
	if namespace:
		return bool(ip.netns(f"exec {namespace} ip link set dev {ifname} master {bridge}").exit_code == 0)
	else:
		return bool(ip.link(f"set dev {ifname} master {bridge}").exit_code == 0)

def ifup(ifname :str) -> bool:
	return bool(ip.link(f"set {ifname} up").exit_code == 0)

def ifdown(ifname :str) -> bool:
	return bool(ip.link(f"set {ifname} down").exit_code == 0)

def get_namespace_info(namespace :Optional[str] = None) -> Dict[str, Any]:
	if (output := SysCommand("ip -oneline -color=never -j netns list")).exit_code == 0:
		if namespace:
			try:
				for info in json.loads(str(output.decode())):
					if info.get('name') == namespace:
						return dict(info)
				raise NamespaceNotFound(f"Could not locate namespace {namespace} in output: {output}")
			except json.decoder.JSONDecodeError:
				raise NamespaceError(f"Could not locate namespace {namespace} in output: {output}")
		else:
			return dict(json.loads(str(output)))
	elif output.exit_code == 256:
		raise NamespaceNotFound(f"Could not locate namespace {namespace} in output: {output}")
	else:
		raise ValueError(f"Could not execute namespace info grabber: {output.exit_code} {output}")

def get_interface_info(ifname :str) -> Optional[Iterator[Dict[str, Union[int, None, str]]]]:
	if info := psutil.net_if_addrs().get(ifname):
		yield {
			"family": {socket.AF_INET: "IPv4", socket.AF_INET6: "IPv6", psutil.AF_LINK: "MAC"}.get(info[0]),
			"address": info[1],
			"netmask": info[2],
			"broadcast": info[3],
			"point_to_point": info[4]
		}
	else:
		raise InterfaceNotFound(f"Could not locate physical interface {ifname}.")

def load_network_info(interfaces :List[Dict[str, Any]] = []) -> None:
	for interface in interfaces:
		if not interface.get('name'):
			raise InterfaceError(f"Loading interfaces require the interface information to have a name key with a str value.")

		if (iftype := interface.get('type')) == 'tap':
			if not (output := ip.tuntap(f"add mode tap one_queue vnet_hdr user 0 group 0 name {interface['name']}")).exit_code == 0:
				raise InterfaceError(f"Could not add tap interface {interface['name']}: [{output.exit_code}] {output}")

		elif iftype == 'veth':
			if not get_interface_info(f"{interface['name']}"):
				pair_name = interface.get('veth_pair', f"{interface['name']}_ns")

				ip.link(f"add {interface['name']} type veth peer name {pair_name}")

		elif iftype == 'phys':
			get_interface_info(interface['name'])

		else:
			raise UnsupportedHardware(f"Unknown interface type {iftype}")

		if namespace := interface.get('namespace'):
			try:
				get_namespace_info(interface['namespace'])
			except (NamespaceNotFound, NamespaceError):
				add_namespace(interface['namespace'])

			ip.link(f"set {interface['name']} netns {interface['namespace']}")

		if interface.get('bridge'):
			add_bridge(f"{interface['bridge']}", namespace=namespace)
			add_if_to_bridge(f"{interface['bridge']}", f"{interface['name']}", namespace=namespace)

def unload_network_info(interfaces :List[Dict[str, Any]] = []) -> None:
	for interface in interfaces:
		if interface.get('namespace'):
			del_namespace(interface['namespace'])
		else:
			if not interface.get('name'):
				raise InterfaceError(f"Loading interfaces require the interface information to have a name key with a str value.")

			ip.link(f"del {interface.get('name')}")

			if interface.get('bridge'):
				ip.link(f"del {interface.get('bridge')}")