from struct import unpack
from nimutool.parser.common import CanParserBase, get_all_subclasses, twos_comp
from nimutool.canbus.can_message import ParsedCanMessage
from dataclasses import dataclass
from typing import Tuple
import math


def unpack_21b_float(val, fraction_bits):
    return twos_comp(val, 21) / 2**fraction_bits


def parse_pi_fixpoint(data, fraction_bits):
    val = unpack('<Q', data)[0]
    vals = [unpack_21b_float((val >> shift) & 0x1fffff, fraction_bits) for shift in [0, 21, 42]]
    return vals


@dataclass
class PI48BaseParams:
    extended: bool = True
    frequency: int = 1


@dataclass
class Pi48Gyroscope(PI48BaseParams):
    canid: int = 0x0c501010
    priority: int = 1
    signals: Tuple[str] = ('pi48gx', 'pi48gy', 'pi48gz')

    def parse(self, data):
        vals = parse_pi_fixpoint(data, 9)
        vals = list(map(math.radians, vals))
        return ParsedCanMessage(None, self.signals, vals, [f'{v:7.7f}' for v in vals])


@dataclass
class Pi48Acceleration(PI48BaseParams):
    canid: int = 0x0c501011
    priority: int = 2
    signals: Tuple[str] = ('pi48ax', 'pi48ay', 'pi48az')

    def parse(self, data):
        vals = parse_pi_fixpoint(data, 11)
        return ParsedCanMessage(None, self.signals, vals, [f'{v:7.7f}' for v in vals])


@dataclass
class Pi48Status:
    canid: int = 0x0c501000
    priority: int = 3
    frequency: int = 10

    def parse(self, data):
        packet_number, temperature, voltage = unpack('<IhH', data)
        temperature /= 2**8
        voltage /= 2**8
        return packet_number, temperature, voltage


@dataclass
class Pi48Firmware:
    canid: int = 0x0c501001
    priority: int = 3
    frequency: int = 10

    def parse(self, data):
        build_date, firmware_version, git_hash = unpack('<HHI', data)
        return build_date, firmware_version, git_hash


@dataclass
class Pi48DeviceInfo:
    canid: int = 0x0c501002
    priority: int = 3
    frequency: int = 10

    def parse(self, data):
        serial_number, human_serial_number, product_id = unpack('<IHH', data)
        return serial_number, human_serial_number, product_id


@dataclass
class Pi48ProtocolInfo:
    canid: int = 0x0c501003
    priority: int = 3
    frequency: int = 10

    def parse(self, data):
        status, gfraction, afraction, packet_rate = unpack('<HxxBBH', data)
        return [status]


class PI48Parser(CanParserBase):

    MSG_HANDLERS = get_all_subclasses(PI48BaseParams)
