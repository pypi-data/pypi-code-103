"""

Sungrow Inverter register reader

Connect to a Sungrow modbus via TCP

Supports Sungrow Hybrid & String inverters

Refer configs/hybrid.py and configs/string.py for inverters that are supported.
"""

__version__ = "0.1.5"

from SungrowModbusTcpClient import SungrowModbusTcpClient

from sungrowinverter.configs.inverter import (
    INVERTER_SCAN,
    INVERTER_READ_REGISTERS,
    INVERTER_HOLDING_REGISTERS,
    INVERTER_MODELS,
)

from sungrowinverter.configs.common import SungrowInverterModel, ModBusRegister

from sungrowinverter.configs.hybrid import (
    HYBRID_SCAN,
    HYBRID_READ_REGISTERS,
    HYBRID_HOLDING_REGISTERS,
)
from sungrowinverter.configs.string import (
    STRING_SCAN,
    STRING_READ_REGISTERS,
    STRING_HOLDING_REGISTERS,
)

import logging

_LOGGING = logging.getLogger(__name__)

REQUESTS_TIMEOUT = 60


class SungrowInverter:
    """
    SungrowInverter module for read modbus data from tcp connect to Sungrow inverters (hybrid / string) inverters supported
    """

    def __init__(self, ip_address, port=502, slave=1, retries=3, timeout=REQUESTS_TIMEOUT):
        """Initialize a Sungrow Inverter TCP Modbus Client object"""
        self.manufacturer = "Sungrow"

        # Set when invert_model is run
        self.model = None
        self.device_code = None
        self.mppt_inputs = 0
        self.serial_number = None
        self.nominal_output_power = None
        self.inverter_type = None

        self.battery_type = None
        self.battery_capacity = None

        self._modbusclient = None
        self._slave = slave
        self._timeout = timeout

        self.data = {}

        client_payload = {
            "host": ip_address,
            "port": port,
            "timeout": timeout,
            "retries": retries,
            "retry_on_empty": True,
        }

        self._modbusclient = SungrowModbusTcpClient.SungrowModbusTcpClient(**client_payload)

        _LOGGING.debug("Sungrow modbus TCP client - [IP:%s Port:%s]", ip_address, port)

    async def _load_registers(self, register_type, start, modbus_registers, count=100):
        try:
            if register_type == "read":
                response = self._modbusclient.read_input_registers(int(start), count=count, unit=self._slave)
            elif register_type == "holding":
                response = self._modbusclient.read_holding_registers(int(start), count=count, unit=self._slave)
            else:
                _LOGGING.error("Unsupported register type: %s", register_type)

        except Exception as err:
            _LOGGING.warning("No data. Try increasing the timeout or scan interval: %s", err, exc_info=1)
            return False

        if response.isError():
            _LOGGING.warning("Modbus connection failed, connection could not be made or register range failed to be read.")
            return False

        if not hasattr(response, "registers"):
            _LOGGING.warning("No registers returned")
            return

        if len(response.registers) != count:
            _LOGGING.warning("Mismatched number of registers read %s != %s", len(response.registers), count)
            return

        _LOGGING.debug("Registers: %s [start_register: %s, register_count: %s] contents: %s", register_type, int(start) + 1, count, response.registers)

        for current_register in modbus_registers:

            if (start + 1) <= current_register.address <= (start + 1 + count):

                if not next((x for x in modbus_registers if x.address == current_register.address), None,) is None:

                    if not current_register.valid_inverters is None:
                        if not self.device_code in current_register.valid_inverters:
                            continue

                    # We want to make sure we only add the neccessary mppt entries we dont need to create data
                    # if the inverter don't support it (most have 2, others 1, 3 or more)
                    if current_register.key.startswith("mppt_"):
                        mppt_key = current_register.key.split("_")
                        if int(mppt_key[1]) > self.mppt_inputs:
                            continue

                    register_index = current_register.address - (start + 1)

                    if current_register.data_type == "U16":
                        value = response.registers[register_index]

                    elif current_register.data_type == "U32":
                        value = (response.registers[register_index + 1] << 16) + response.registers[register_index]

                    elif current_register.data_type == "S16":
                        value = int.from_bytes(response.registers[register_index].to_bytes(2, "little"), "little", signed=True)

                    elif current_register.data_type == "S32":
                        value = int.from_bytes(((response.registers[register_index + 1] << 16) + response.registers[register_index]).to_bytes(4, "little"), "little", signed=True)

                    elif current_register.data_type == "UTF8":
                        value = await self._get_utf8(response.registers, register_index, current_register.length)

                    else:
                        _LOGGING.debug("Unknown data_type used for register %s [register: %s data_type: %s]",
                                        current_register.key, current_register.address, current_register.data_type)

                    if current_register.unit_precision is not None:
                        value = round(value * current_register.unit_precision, 1)

                    if current_register.table is not None:

                        # if we need to decode a returned value into a set of binary information
                        # table hold binary map
                        # value here will contain the bits to translate against the binary map
                        if current_register.transform == "BINARY":
                            # we will set each bit into a value ie. whether something is on or off usually.
                            binary_map = current_register.table
                            bit_val = 1
                            while bit_val < 2 ** int(current_register.length):
                                if bit_val in binary_map:
                                    if value & bit_val == bit_val:
                                        self.data[binary_map[bit_val]] = True
                                    else:
                                        self.data[binary_map[bit_val]] = False
                                bit_val = bit_val << 1
                        else:
                            #if value in current_register.table:
                            self.data[current_register.key] = current_register.table[value]

                    else:
                        self.data[current_register.key] = value

        return True

    async def _get_utf8(self, registers, index, length):

        buff = b""
        for byte in range(index, length):
            buff += bytes(int(registers[byte]).to_bytes(2, byteorder="big"))

        if bytes(buff).find(b"\0", 0):
            end = bytes(buff).find(b"\0")
            if end != -1:
                return bytes(buff)[0:end].decode("utf-8")

        return ""

    async def inverter_model(self) -> SungrowInverterModel:
        """Connect to the inverter and scrape the inverter model and serial data"""

        # if first time run then get the model details and load the relevant modmap for the model for future requests
        # if we fail to connect then do nothing and exit
        if self.model is None:

            self._modbusclient.connect()

            # load the inverter registers to get static data, and determine if model found is supported.
            for scan_type in INVERTER_SCAN["read"]:
                if not await self._load_registers("read", scan_type["scan_start"], INVERTER_READ_REGISTERS, scan_type["scan_range"]):
                    return False

            self._modbusclient.close()

            if "device_type_code" in self.data:
                inverter_model = next((x for x in INVERTER_MODELS if x.device_code == self.data["device_type_code"]), None,)

                if inverter_model is not None:
                    self.model = inverter_model.model
                    self.data["model"] = inverter_model.model
                    self.inverter_type = inverter_model.inverter_type
                    self.mppt_inputs = inverter_model.mppt_inputs
                    self.serial_number = self.data["serial_number"]
                    self.nominal_output_power = f"{self.data['nominal_output_power']} kW"
                    inverter_model.nominal_output_power = self.nominal_output_power
                    inverter_model.serial_number = self.serial_number
                    self.device_code = self.data['device_type_code']

                    _LOGGING.info(
                        "Sungrow residential inverter found: [Device Code: %s, Model: %s, Nominal Ouput: %s, Serial# %s]",
                        hex(inverter_model.device_code),
                        inverter_model.model,
                        inverter_model.nominal_output_power,
                        inverter_model.serial_number,
                    )

                    # see if the inverter supports a battery if so grab that data also
                    if inverter_model.inverter_type == "hybrid":
                        self._modbusclient.connect()

                        # load the inverter registers to get static data, and determine if model found is supported.
                        for scan_type in INVERTER_SCAN["holding"]:
                            if not await self._load_registers("holding", scan_type["scan_start"], INVERTER_HOLDING_REGISTERS, scan_type["scan_range"]):
                                return False

                        self._modbusclient.close()

                        if "battery_type" in self.data:
                            self.battery_type = self.data["battery_type"]
                            self.battery_capacity = round((self.data["battery_nominal_voltage"] * self.data["battery_capacity"]) / 1000, 1)
                            self.data["battery_capacity"] = self.battery_capacity

                        _LOGGING.info("Storage device attached to inverter: [Model: %s, Capacity: %s kWh]", self.battery_type, self.battery_capacity)
                    return inverter_model

                _LOGGING.error("Supported inverter device type code %s was not found in our supported devices", self.data["device_type_code"])
        else:
            return SungrowInverterModel(self.device_code, self.model, self.inverter_type, self.mppt_inputs, self.nominal_output_power, self.serial_number)

        return None

    # Core monitoring loop
    async def async_update(self):
        """Connect to the inverter and scrape the metrics"""

        if self.model is None:
            await self.inverter_model()

        if self.model is not None:

            if self.inverter_type == "hybrid":
                inverter_scan = HYBRID_SCAN
                read_registers = HYBRID_READ_REGISTERS
                holding_registers = HYBRID_HOLDING_REGISTERS
            elif self.inverter_type == "string":
                inverter_scan = STRING_SCAN
                read_registers = STRING_READ_REGISTERS
                holding_registers = STRING_HOLDING_REGISTERS
            else:
                _LOGGING.error("Inverter type is not supported")
                return False

            self._modbusclient.connect()

            for scan_type, scan_settings in inverter_scan.items():
                for scan in scan_settings:
                    if not await self._load_registers(scan_type,
                                                      scan["scan_start"],
                                                      read_registers if scan_type == "read" else holding_registers,
                                                      int(scan["scan_range"])):
                        return False

            self._modbusclient.close()

            try:
                self.data["timestamp"] = '%s/%s/%s %02d:%02d:%02d' % (
                    self.data["year"], self.data["month"], self.data["day"],
                    self.data["hour"], self.data["minute"], self.data["second"])
            except Exception:
                pass

        _LOGGING.debug("DEBUG: scraped data %s", self.data)
        return True
