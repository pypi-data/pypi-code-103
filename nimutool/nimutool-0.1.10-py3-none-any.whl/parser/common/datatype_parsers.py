from nimutool.canbus.can_message import ParsedCanMessage
from struct import unpack


def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)         # compute negative value
    return val                          # return positive value as is


class ParseOneDouble:

    def parse(self, data) -> ParsedCanMessage:
        if len(data) == 8:
            val = unpack('<d', data)[0]
            return ParsedCanMessage(None, self.signals, (val,), (f'{val:.6f}',))


class ParseTwoIntegers:

    def parse(self, data) -> ParsedCanMessage:
        if len(data) == 8:
            vals = unpack('<II', data)
            return ParsedCanMessage(None, self.signals, vals, (str(v) for v in vals))


class ParseTwoFloats:

    def parse(self, data) -> ParsedCanMessage:
        if len(data) == 8:
            vals = unpack('<ff', data)
            return ParsedCanMessage(None, self.signals, vals, (f'{v:.6f}' for v in vals))


class ParseFixPointError:

    @staticmethod
    def _is_high_range(number: int):
        return number & (1 << 60) != 0

    @staticmethod
    def _unpack_20b_float(val, range_hi):
        shift = 13 if range_hi else 15
        return twos_comp(val, 20) / (1 << shift)

    @staticmethod
    def _parse_fixpoint(data):
        val = unpack('<Q', data)[0]
        vals = [ParseFixPointError._unpack_20b_float((val >> shift) & 0xfffff, ParseFixPointError._is_high_range(val)) for shift in [0, 20, 40]]
        error_flags = [val & (1 << i) != 0 for i in range(61, 64)]
        return vals, error_flags

    def parse(self, data) -> ParsedCanMessage:
        if len(data) == 8:
            vals, errors = ParseFixPointError._parse_fixpoint(data)
            return ParsedCanMessage(None, self.signals, vals + errors, [f'{v:.6f}' for v in vals] + [str(int(e)) for e in errors])


class ParseFixPoint(ParseFixPointError):

    def parse(self, data) -> ParsedCanMessage:
        if len(data) == 8:
            vals, _ = ParseFixPoint._parse_fixpoint(data)
            return ParsedCanMessage(None, self.signals, vals, (f'{v:.6f}' for v in vals))
