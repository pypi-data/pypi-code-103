# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from .generated import Svm41I2cCmdGetVersion as GetVersionGenerated
from .generated import Svm41I2cCmdReadMeasuredValuesAsIntegers as \
    ReadMeasuredValuesAsIntGenerated
from .generated import \
    Svm41I2cCmdReadMeasuredRawValues as \
    ReadMeasuredValuesAsIntRawGenerated
from .generated import Svm41I2cCmdGetTemperatureOffsetForRhtMeasurements as \
    GetTOffsetGenerated
from .generated import Svm41I2cCmdSetTemperatureOffsetForRhtMeasurements as \
    SetTOffsetGenerated
from ..version_types import FirmwareVersion, HardwareVersion, \
    ProtocolVersion, Version
from ..response_types import AirQualityVoc, AirQualityNox, Humidity, \
    Temperature

import logging
log = logging.getLogger(__name__)


class Svm41I2cCmdGetVersion(GetVersionGenerated):
    """
    Get Version I²C Command

    Gets the version information for the hardware, firmware and protocol.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Svm41I2cCmdGetVersion, self).__init__()

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data: Received raw bytes from the read operation.
        :return: The device version as a Version object.
        :rtype: ~sensirion_i2c_svm41.version_types.Version
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        firmware_major, firmware_minor, firmware_debug, hardware_major, \
            hardware_minor, protocol_major, protocol_minor, _ = \
            GetVersionGenerated.interpret_response(self, data)
        return Version(
            firmware=FirmwareVersion(
                major=firmware_major,
                minor=firmware_minor,
                debug=firmware_debug
            ),
            hardware=HardwareVersion(
                major=hardware_major,
                minor=hardware_minor
            ),
            protocol=ProtocolVersion(
                major=protocol_major,
                minor=protocol_minor
            )
        )


class Svm41I2cCmdGetTemperatureOffsetForRhtMeasurements(GetTOffsetGenerated):
    """
    Get Temperature Offset For Rht Measurements I²C Command

    Gets the T-Offset for the temperature compensation of the RHT algorithm.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Svm41I2cCmdGetTemperatureOffsetForRhtMeasurements, self) \
            .__init__()

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return: Temperature offset in degrees celsius.
        :rtype: float
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """
        result = GetTOffsetGenerated.interpret_response(self, data)
        return float(result) / 200.  # scaled int16


class Svm41I2cCmdSetTemperatureOffsetForRhtMeasurements(SetTOffsetGenerated):
    """
    Set Temperature Offset For Rht Measurements I²C Command

    Sets the T-Offset for the temperature compensation of the RHT algorithm.
    """

    def __init__(self, t_offset):
        """
        Constructor.

        :param float t_offset: Temperature offset in degrees celsius.
        """
        super(Svm41I2cCmdSetTemperatureOffsetForRhtMeasurements, self) \
            .__init__(int(round(t_offset * 200)))  # scaled int16


class Svm41I2cCmdReadMeasuredValues(ReadMeasuredValuesAsIntGenerated):
    """
    Returns the new measurement results.

    .. note:: This command is only available in measurement mode. The firmware
              updates the measurement values every second. Polling data with a
              faster sampling rate will return the same values. The first
              measurement is available 1 second after the start measurement
              command is issued. Any readout prior to this will return zero
              initialized values.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Svm41I2cCmdReadMeasuredValues, self).__init__()

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return:
            The measured humidity, temperature, voc and nox air quality.

            - humidity (:py:class:`~sensirion_i2c_svm41.response_types.Humidity`) -
              Humidity response object.
            - temperature (:py:class:`~sensirion_i2c_svm41.response_types.Temperature`) -
              Temperature response object.
            - air_quality_voc (:py:class:`~sensirion_i2c_svm41.response_types.AirQualityVoc`) -
              Air quality voc response object.
            - air_quality_nox (:py:class:`~sensirion_i2c_svm41.response_types.AirQualityNox`) -
              Air quality nox response object.
        :rtype:
            tuple
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """  # noqa: E501
        humidity, temperature, air_quality_voc, air_quality_nox = \
            ReadMeasuredValuesAsIntGenerated.interpret_response(self, data)
        return Humidity(humidity), Temperature(temperature), \
            AirQualityVoc(air_quality_voc), AirQualityNox(air_quality_nox)


class Svm41I2cCmdReadMeasuredValuesRaw(ReadMeasuredValuesAsIntRawGenerated):
    """
    Returns the new measurement results with raw values added.

    .. note:: This command is only available in measurement mode. The firmware
              updates the measurement values every second. Polling data with a
              faster sampling rate will return the same values. The first
              measurement is available 1 second after the start measurement
              command is issued. Any readout prior to this will return zero
              initialized values.
    """

    def __init__(self):
        """
        Constructor.
        """
        super(Svm41I2cCmdReadMeasuredValuesRaw, self).__init__()

    def interpret_response(self, data):
        """
        Validates the CRCs of the received data from the device and returns
        the interpreted data.

        :param bytes data:
            Received raw bytes from the read operation.
        :return:
            The measured air quality, humidity and temperature including the
            raw values without algorithm compensation.
            - humidity (:py:class:`~sensirion_i2c_svm41.response_types.Humidity`) -
              Humidity response object.
            - temperature (:py:class:`~sensirion_i2c_svm41.response_types.Temperature`) -
              Temperature response object.
            - raw_voc_ticks (:py:class:`~sensirion_i2c_svm41.response_types.AirQualityVoc`) -
              Raw VOC output ticks as read from the SGP sensor.
            - raw_nox_ticks (:py:class:`~sensirion_i2c_svm41.response_types.AirQualityNox`) -
              Raw NOx output ticks as read from the SGP sensor.

        :rtype:
            tuple
        :raise ~sensirion_i2c_driver.errors.I2cChecksumError:
            If a received CRC was wrong.
        """  # noqa: E501

        raw_humidity, raw_temperature, raw_voc_ticks, raw_nox_ticks =\
            ReadMeasuredValuesAsIntRawGenerated.interpret_response(self, data)
        return Humidity(raw_humidity), Temperature(raw_temperature), \
            raw_voc_ticks, raw_nox_ticks
