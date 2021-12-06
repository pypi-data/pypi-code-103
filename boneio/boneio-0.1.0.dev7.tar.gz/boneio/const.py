# from typing import Literal
from typing_extensions import Literal
from datetime import timedelta

DEBOUNCE_DURATION = timedelta(seconds=0.2)
LONG_PRESS_DURATION = timedelta(seconds=0.7)
DELAY_DURATION = 0.1
SECOND_DELAY_DURATION = 0.3
RELAY = "relay"
SINGLE = "single"
DOUBLE = "double"
LONG = "long"
ONLINE = "online"
ON = "ON"
OFF = "OFF"
STATE = "state"
PAHO = "paho.mqtt.client"
ClickTypes = Literal[SINGLE, DOUBLE, LONG]
MQTT = "mqtt"
HOST = "host"
USERNAME = "username"
PASSWORD = "password"
TOPIC_PREFIX = "topic_prefix"
HA_DISCOVERY = "ha_discovery"
ENABLED = "enabled"
GPIO_INPUT = "gpio_input"
OUTPUT = "output"
PIN = "pin"
ID = "id"
KIND = "kind"
GPIO = "gpio"
ACTIONS = "actions"
ACTION = "action"
OUTPUT = "output"
ADDRESS = "address"
MCP23017 = "mcp23017"
SWITCH = "switch"
CONFIG_PIN = "/usr/bin/config-pin"
MCP = "mcp"
MCP_ID = "mcp_id"
HA_TYPE = "ha_type"
GIGABYTE = 1073741824
MEGABYTE = 1048576
OLED_PIN = "P9_41"
NUM_OF_SCREENS = 6
WIDTH = 128
UPTIME = "uptime"
NETWORK = "network"
CPU = "cpu"
DISK = "disk"
MEMORY = "memory"
SWAP = "swap"
WHITE = "white"
OLED = "oled"
OledDataTypes = Literal[UPTIME, NETWORK, CPU, DISK, MEMORY, SWAP, OUTPUT]
