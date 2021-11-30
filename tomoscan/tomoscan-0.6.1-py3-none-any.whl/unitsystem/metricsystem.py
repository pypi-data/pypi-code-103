# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2020 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "01/09/2016"


from silx.utils.enum import Enum as _Enum

# Constants
_elementary_charge_coulomb = 1.602176634e-19


_joule_si = 1.0


class EnergySI(_Enum):
    """Util enum for energy in SI units (Joules)"""

    JOULE = _joule_si
    ELEMCHARGE = _elementary_charge_coulomb
    ELECTRONVOLT = _elementary_charge_coulomb

    KILOELECTRONVOLT = _elementary_charge_coulomb * 1e3
    MEGAELECTRONVOLT = _elementary_charge_coulomb * 1e6
    GIGAELECTRONVOLT = _elementary_charge_coulomb * 1e9
    KILOJOULE = 1e3 * _joule_si

    @classmethod
    def from_value(cls, value):
        if isinstance(value, str):
            return cls.from_str(value=value)
        else:
            _Enum.from_value(value=value)

    @classmethod
    def from_str(cls, value: str):
        assert isinstance(value, str)
        if value.lower() in ("e", "qe"):
            return EnergySI.ELEMCHARGE
        elif value.lower() in ("j", "joule"):
            return EnergySI.JOULE
        elif value.lower() in ("kj", "kilojoule"):
            return EnergySI.KILOJOULE
        elif value.lower() in ("ev", "electronvolt"):
            return EnergySI.ELECTRONVOLT
        elif value.lower() in ("kev", "kiloelectronvolt"):
            return EnergySI.KILOELECTRONVOLT
        elif value.lower() in ("mev", "megaelectronvolt"):
            return EnergySI.MEGAELECTRONVOLT
        elif value.lower() in ("gev", "gigaelectronvolt"):
            return EnergySI.GIGAELECTRONVOLT
        else:
            raise ValueError("Cannot convert: %s" % value)


# Default units:
#  - lenght: meter (m)
#  - energy: kilo Electronvolt (keV)
_meter = 1.0
_kev = 1.0
_joule_kev = 1.0 / EnergySI.KILOELECTRONVOLT.value


class MetricSystem(_Enum):
    """Util enum to retrieve metric"""

    METER = _meter
    m = _meter
    CENTIMETER = _meter / 100.0
    MILLIMETER = _meter / 1000.0
    MICROMETER = _meter * 1e-6
    NANOMETER = _meter * 1e-9

    KILOELECTRONVOLT = _kev
    ELECTRONVOLT = _kev * 1e-3
    JOULE = _kev / EnergySI.KILOELECTRONVOLT.value
    KILOJOULE = _kev / EnergySI.KILOELECTRONVOLT.value * 1e3

    @classmethod
    def from_value(cls, value):
        if isinstance(value, str):
            return cls.from_str(value=value)
        else:
            return _Enum.from_value(value=value)

    @classmethod
    def from_str(cls, value: str):
        assert isinstance(value, str)
        if value.lower() in ("m", "meter"):
            return MetricSystem.METER
        elif value.lower() in ("cm", "centimeter"):
            return MetricSystem.CENTIMETER
        elif value.lower() in ("mm", "millimeter"):
            return MetricSystem.MILLIMETER
        elif value.lower() in ("um", "micrometer", "microns"):
            return MetricSystem.MICROMETER
        elif value.lower() in ("nm", "nanometer"):
            return MetricSystem.NANOMETER
        elif value.lower() in ("kev", "kiloelectronvolt"):
            return MetricSystem.KILOELECTRONVOLT
        elif value.lower() in ("ev", "electronvolt"):
            return MetricSystem.ELECTRONVOLT
        elif value.lower() in ("j", "joule"):
            return MetricSystem.JOULE
        elif value.lower() in ("kj", "kilojoule"):
            return MetricSystem.KILOJOULE
        else:
            raise ValueError("Cannot convert: %s" % value)

    def __str__(self):
        if self == MetricSystem.METER:
            return "m"
        elif self == MetricSystem.CENTIMETER:
            return "cm"
        elif self == MetricSystem.MILLIMETER:
            return "mm"
        elif self == MetricSystem.MICROMETER:
            return "um"
        elif self == MetricSystem.NANOMETER:
            return "nm"
        elif self == MetricSystem.KILOELECTRONVOLT:
            return "keV"
        elif self == MetricSystem.ELECTRONVOLT:
            return "eV"
        elif self == MetricSystem.JOULE:
            return "J"
        elif self == MetricSystem.KILOJOULE:
            return "kJ"
        else:
            raise ValueError("Cannot convert: %s" % value)


m = MetricSystem.METER
meter = MetricSystem.METER

centimeter = MetricSystem.CENTIMETER
cm = centimeter

millimeter = MetricSystem.MILLIMETER
mm = MetricSystem.MILLIMETER

micrometer = MetricSystem.MICROMETER

nanometer = MetricSystem.NANOMETER
