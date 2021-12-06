import json
import pathlib
from typing import Dict, Any

from .networking import load_network_info, unload_network_info

def load_conf(config :str) -> Dict[str, Any]:
	config_path = pathlib.Path(config).expanduser().absolute()

	with config_path.open('r') as fh:
		configuration = json.load(fh)

	return dict(configuration)

def load_environment(config :str) -> None:
	configuration = load_conf(config)

	if configuration.get('interfaces'):
		load_network_info(interfaces=configuration['interfaces'])

def dismantle_environment(config :str) -> None:
	configuration = load_conf(config)

	if configuration.get('interfaces'):
		unload_network_info(interfaces=configuration['interfaces'])