from nimutool.parser.common import CanParserBase, ParseFixPoint, ParseFixPointError, get_all_subclasses
from nimutool.canbus.can_message import ParsedCanMessage
from struct import unpack
from typing import Tuple, List
from dataclasses import dataclass


@dataclass
class NimuBaseParams:
    extended: bool = False
    frequency: int = 1


@dataclass
class Sync(NimuBaseParams):
    canid: int = 0x000
    priority: int = 1
    signals: Tuple[str] = ('gpstime',)

    def parse(self, data) -> ParsedCanMessage:
        if len(data) == 8:
            vals = unpack('<II', data)
            t = vals[0] + vals[1] / 1e9
            return ParsedCanMessage(None, self.signals, [t], (f'{t:7.6f}',))
        return ParsedCanMessage(None, self.signals, [0], (f'{0.0:.1f}',))


@dataclass
class HPCAAcceleration(NimuBaseParams, ParseFixPointError):
    canid: int = 0x010
    priority: int = 2
    signals: Tuple[str] = ('hax', 'hay', 'haz', 'haxe', 'haye', 'haze')


@dataclass
class HPCAGyroscope(NimuBaseParams, ParseFixPointError):
    canid: int = 0x020
    priority: int = 3
    signals: Tuple[str] = ('hgx', 'hgy', 'hgz', 'hgxe', 'hgye', 'hgze')


@dataclass
class HPCAStatus(NimuBaseParams):
    canid: int = 0x040
    priority: int = 4
    signals: Tuple[str] = ('ht',)

    def parse(self, data) -> ParsedCanMessage:
        temp = unpack('h3h', data)[0]
        vals = (temp / 10,)
        return ParsedCanMessage(None, self.signals, vals, (f'{vals[0]:7.6f}',))


@dataclass
class BMXAcceleration(NimuBaseParams, ParseFixPointError):
    canid: int = 0x090
    priority: int = 5
    signals: Tuple[str] = ('bax', 'bay', 'baz', 'baxe', 'baye', 'baze')


@dataclass
class BMXGyroscope(NimuBaseParams, ParseFixPointError):
    canid: int = 0x0a0
    priority: int = 6
    signals: Tuple[str] = ('bgx', 'bgy', 'bgz', 'bgxe', 'bgye', 'bgze')


@dataclass
class BMXStatus(HPCAStatus):
    canid: int = 0x0c0
    priority: int = 7
    signals: Tuple[str] = ('bt',)


@dataclass
class HPIAcceleration(NimuBaseParams, ParseFixPointError):
    canid: int = 0x110
    priority: int = 8
    signals: Tuple[str] = ('pax', 'pay', 'paz', 'paxe', 'paye', 'paze')


@dataclass
class DCM1(NimuBaseParams, ParseFixPoint):
    canid: int = 0x400
    priority: int = 11
    signals: Tuple[str] = ('dcm11', 'dcm12', 'dcm13')


@dataclass
class DCM2(NimuBaseParams, ParseFixPoint):
    canid: int = 0x390
    priority: int = 11
    signals: Tuple[str] = ('dcm21', 'dcm22', 'dcm23')


@dataclass
class DCM3(NimuBaseParams, ParseFixPoint):
    canid: int = 0x300
    priority: int = 11
    signals: Tuple[str] = ('dcm31', 'dcm32', 'dcm33')


@dataclass
class Innovation(NimuBaseParams, ParseFixPoint):
    canid: int = 0x340
    priority: int = 12
    signals: Tuple[str] = ('innox', 'innoy', 'innoz')


@dataclass
class Position(NimuBaseParams, ParseFixPoint):
    canid: int = 0x310
    priority: int = 12
    signals: Tuple[str] = ('posz', 'posy', 'posz')


@dataclass
class Velocity(NimuBaseParams, ParseFixPoint):
    canid: int = 0x320
    priority: int = 12
    signals: Tuple[str] = ('velx', 'vely', 'velz')


@dataclass
class ImuPosition(NimuBaseParams):
    canid: int = 0x330
    priority: int = 13
    signals: Tuple[str] = ('imulocid', 'imuposx', 'imuposy', 'imuposz')

    def parse(self, data):
        nid, x, y, z = unpack('<Bxhhh', data)
        vals = [nid, x / 100, y / 100, z / 100]
        return ParsedCanMessage(None, self.signals, vals, (f'{v:.2f}' for v in vals))


@dataclass
class GBias(NimuBaseParams, ParseFixPoint):
    canid: int = 0x410
    priority: int = 12
    signals: Tuple[str] = ('gbiasx', 'gbiasy', 'gbiasz')


@dataclass
class Ascale(NimuBaseParams, ParseFixPoint):
    canid: int = 0x420
    priority: int = 12
    signals: Tuple[str] = ('ascalex', 'ascaley', 'ascalez')


@dataclass
class EKFStatus(NimuBaseParams):
    canid: int = 0x430
    priority: int = 12
    signals: Tuple[str] = ('ekf_update_mode',)

    def parse(self, data):
        mode, _, _, _ = unpack('<BBhI', data)
        return ParsedCanMessage(None, self.signals, [mode], (str(mode),))


@dataclass
class GPSTimePulseStatus(NimuBaseParams):
    canid: int = 0x500
    priority: int = 13
    frequency: int = 1000
    signals: Tuple[str] = ('gps_tp_status', 'gps_tp_error_us', 'gps_tp_vco_tune', 'gps_tp_cycles')

    def parse(self, data):
        status, error_us, pll_tune, clock_cycle_counter = unpack('<BhbI', data)
        vals = (status, error_us, pll_tune, clock_cycle_counter)
        return ParsedCanMessage(None, self.signals, vals, (str(v) for v in vals))


class NimuParser(CanParserBase):

    MSG_HANDLERS = get_all_subclasses(NimuBaseParams)

    def canid2dataid(self, can_id):
        return can_id & 0xff0

    def split_canid_to_msgid_and_nodeid(self, can_id):
        return can_id & 0xff0, can_id & 0x00f

    def contains_sync(self, can_ids: List[int]):
        return Sync.canid in can_ids

    def is_sync(self, can_id: int):
        return can_id == Sync.canid


class NimuDebugBaseParams(NimuBaseParams):
    extended: bool = False
    frequency: int = 1
    priority: int = 1
    frequency: int = 1


@dataclass
class NimuDebugMessage(NimuDebugBaseParams):
    canid: int = 0x3d0
    signals: Tuple[str] = ('debug',)

    def parse(self, data):
        line = data.decode(errors="replace")
        return ParsedCanMessage(None, self.signals, [line], [line])


class NimuDebugParser(NimuParser):

    MSG_HANDLERS = get_all_subclasses(NimuDebugBaseParams)
