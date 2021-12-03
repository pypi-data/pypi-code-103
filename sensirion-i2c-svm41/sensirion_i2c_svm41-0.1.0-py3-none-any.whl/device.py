# -*- coding: utf-8 -*-
# (c) Copyright 2021 Sensirion AG, Switzerland

from __future__ import absolute_import, division, print_function
from sensirion_i2c_driver import I2cDevice
from .commands import Svm41I2cCmdGetSerialNumber, Svm41I2cCmdDeviceReset, \
    Svm41I2cCmdGetVersion, Svm41I2cCmdStartMeasurement, \
    Svm41I2cCmdStopMeasurement, Svm41I2cCmdReadMeasuredValues, \
    Svm41I2cCmdReadMeasuredValuesRaw, \
    Svm41I2cCmdGetTemperatureOffsetForRhtMeasurements, \
    Svm41I2cCmdSetTemperatureOffsetForRhtMeasurements, \
    Svm41I2cCmdGetVocAlgorithmTuningParameters, \
    Svm41I2cCmdSetVocAlgorithmTuningParameters, \
    Svm41I2cCmdGetVocAlgorithmState, Svm41I2cCmdSetVocAlgorithmState, \
    Svm41I2cCmdGetNoxAlgorithmTuningParameters, \
    Svm41I2cCmdSetNoxAlgorithmTuningParameters, \
    Svm41I2cCmdStoreNvData


class Svm41I2cDevice(I2cDevice):
    """
    SVM41 I²C device class to allow executing I²C commands.
    """

    def __init__(self, connection, slave_address=0x6A):
        """
        Constructs a new SVM41 I²C device.

        :param ~sensirion_i2c_driver.connection.I2cConnection connection:
            The I²C connection to use for communication.
        :param byte slave_address:
            The I²C slave address, defaults to 0x6A.
        """
        super(Svm41I2cDevice, self).__init__(connection, slave_address)

    def device_reset(self):
        """
        Execute a device reset (reboot firmware, similar to power cycle).
        """
        return self.execute(Svm41I2cCmdDeviceReset())

    def get_serial_number(self):
        """
        Get the serial number of the device.

        :return: The serial number as an ASCII string.
        :rtype: string
        """
        return self.execute(Svm41I2cCmdGetSerialNumber())

    def get_version(self):
        """
        Get the version of the device firmware, hardware and SHDLC protocol.

        :return: The device version.
        :rtype: ~sensirion_i2c_svm41.response_types.Version
        """
        return self.execute(Svm41I2cCmdGetVersion())

    def get_compensation_temperature_offset(self):
        """
        Gets the temperature offset for RHT measurements.

        :return: Temperature offset in degrees celsius.
        :rtype: float
        """
        return self.execute(
            Svm41I2cCmdGetTemperatureOffsetForRhtMeasurements())

    def set_compensation_temperature_offset(self, t_offset):
        """
        Sets the temperature offset for RHT measurements.

        .. note:: Execute the command
            :py:meth:`~sensirion_i2c_svm41.device.store_nv_data` command
            after writing the parameter to store it in the non-volatile memory
            of the device otherwise the parameter will be reset upton a device
            reset.

        :param float t_offset: Temperature offset in degrees celsius.
        """
        return self.execute(
            Svm41I2cCmdSetTemperatureOffsetForRhtMeasurements(t_offset))

    def get_voc_tuning_parameters(self):
        """
        Gets the currently set parameters for customizing the VOC algorithm.

        :return:
            - voc_index_offset (int) -
              VOC index representing typical (average) conditions.
            - learning_time_offset_hours (int) -
              Time constant to estimate the VOC algorithm offset from the
              history in hours. Past events will be forgotten after about twice
              the learning time.
            - learning_time_gain_hours (int) -
              Time constant to estimate the VOC algorithm gain from the history
              in hours. Past events will be forgotten after about twice the
              learning time.
            - gating_max_duration_minutes (int) -
              Maximum duration of gating in minutes (freeze of estimator during
              high VOC index signal). Zero disables the gating.
            - std_initial (int) -
              Initial estimate for standard deviation. Lower value boosts
              events during initial learning period, but may result in larger
              device-to-device variations.
            - gain_factor (int) -
              Factor to amplify or to attenuate the VOC Index output.
        :rtype: tuple
        """
        return self.execute(Svm41I2cCmdGetVocAlgorithmTuningParameters())

    def set_voc_tuning_parameters(self, voc_index_offset,
                                  learning_time_offset_hours,
                                  learning_time_gain_hours,
                                  gating_max_duration_minutes, std_initial,
                                  gain_factor):
        """
        Sets parameters to customize the VOC algorithm. This command is only
        available in idle mode.

        .. note:: Execute the command
                  :py:meth:`~sensirion_i2c_svm41.device.store_nv_data` after
                  writing the parameter to store it in the non-volatile memory
                  of the device otherwise the parameter will be reset upton a
                  device reset.

        :param int voc_index_offset:
            VOC index representing typical (average) conditions. Allowed values
            are in range 1..250. The default value is 100.
        :param int learning_time_offset_hours:
            Time constant to estimate the VOC algorithm offset from the history
            in hours. Past events will be forgotten after about twice the
            learning time. Allowed values are in range 1..1000. The default
            value is 12 hours.
        :param int learning_time_gain_hours:
            Time constant to estimate the VOC algorithm gain from the history
            in hours. Past events will be forgotten after about twice the
            learning time. Allowed values are in range 1..1000. The default
            value is 12 hours.
        :param int gating_max_duration_minutes:
            Maximum duration of gating in minutes (freeze of estimator during
            high VOC index signal). Set to zero to disable the gating. Allowed
            values are in range 0..3000. The default value is 180 minutes.
        :param int std_initial:
            Initial estimate for standard deviation. Lower value boosts events
            during initial learning period, but may result in larger
            device-to-device variations. Allowed values are in range 10..5000.
            The default value is 50.
        :param int gain_factor:
            Gain factor to amplify or to attenuate the VOC index output.
            Allowed values are in range 1..1000. The default value is 230.
        """
        return self.execute(Svm41I2cCmdSetVocAlgorithmTuningParameters(
            voc_index_offset, learning_time_offset_hours,
            learning_time_gain_hours, gating_max_duration_minutes,
            std_initial, gain_factor))

    def get_nox_tuning_parameters(self):
        """
        Gets the currently set parameters for customizing the NOx algorithm.

        :return:
            - nox_index_offset (int) -
              NOx index representing typical (average) conditions.
            - learning_time_offset_hours (int) -
              Time constant to estimate the NOx algorithm offset from the
              history in hours. Past events will be forgotten after about twice
              the learning time.
            - learning_time_gain_hours (int) -
              The time constant to estimate the NOx algorithm gain from the
              history has no impact for NOx. This parameter is still in place
              for consistency reasons with the VOC tuning parameters command.
              This getter will always return the default value.
            - gating_max_duration_minutes (int) -
              Maximum duration of gating in minutes (freeze of estimator during
              high NOx index signal). Zero disables the gating.
            - std_initial (int) -
              The initial estimate for standard deviation has no impact for
              NOx. This parameter is still in place for consistency reasons
              with the VOC tuning parameters command. This getter will always
              return the default value.
            - gain_factor (int) -
              Factor to amplify or to attenuate the NOx Index output.
        :rtype: tuple
        """
        return self.execute(Svm41I2cCmdGetNoxAlgorithmTuningParameters())

    def set_nox_tuning_parameters(self, nox_index_offset,
                                  learning_time_offset_hours,
                                  learning_time_gain_hours,
                                  gating_max_duration_minutes, std_initial,
                                  gain_factor):
        """
        Sets parameters to customize the NOx algorithm. This command is only
        available in idle mode.

        .. note:: Execute the store command after writing the parameter to
                  store it in the non-volatile memory of the device otherwise
                  the parameter will be reset upton a device reset.

        :param int nox_index_offset:
            NOx index representing typical (average) conditions. Allowed values
            are in range 1..250. The default value is 1.
        :param int learning_time_offset_hours:
            Time constant to estimate the NOx algorithm offset from the history
            in hours. Past events will be forgotten after about twice the
            learning time. Allowed values are in range 1..1000. The default
            value is 12 hours.
        :param int learning_time_gain_hours:
            The time constant to estimate the NOx algorithm gain from the
            history has no impact for the NOx algorithm. This parameter is
            still in place for consistency reasons with the VOC tuning
            parameters command. This parameter must always be set to 12 hours.
        :param int gating_max_duration_minutes:
            Maximum duration of gating in minutes (freeze of estimator during
            high NOx index signal). Set to zero to disable the gating. Allowed
            values are in range 0..3000. The default value is 720 minutes.
        :param int std_initial:
            The initial estimate for standard deviation parameter has no impact
            for the NOx algorithm. This parameter is still in place for
            consistency reasons with the VOC tuning parameters command. This
            parameter must always be set to 50.
        :param int gain_factor:
            Gain factor to amplify or to attenuate the VOC index output.
            Allowed values are in range 1..1000. The default value is 230.
        """
        self.execute(Svm41I2cCmdSetNoxAlgorithmTuningParameters(
            nox_index_offset, learning_time_offset_hours,
            learning_time_gain_hours, gating_max_duration_minutes,
            std_initial, gain_factor))

    def store_nv_data(self):
        """
        Stores all customer engine parameters to the non-volatile memory.
        """
        return self.execute(Svm41I2cCmdStoreNvData())

    def get_voc_state(self):
        """
        Gets the current VOC algorithm state. Retrieved values can be used to
        set the VOC algorithm state to resume operation after a short
        interruption, skipping initial learning phase. This command is only
        available during measurement mode.

        .. note:: This feature can only be used after at least 3 hours of
                  continuous operation.

        :return: Current VOC algorithm state.
        :rtype: bytes
        """
        return self.execute(Svm41I2cCmdGetVocAlgorithmState())

    def set_voc_state(self, state):
        """
        Set previously retrieved VOC algorithm state to resume operation after
        a short interruption, skipping initial learning phase. This command is
        only available in idle mode.

        .. note:: This feature should not be used after interruptions of more
                  than 10 minutes.

        :param bytes state: Current VOC algorithm state.
        """
        return self.execute(Svm41I2cCmdSetVocAlgorithmState(state))

    def start_measurement(self):
        """
        Starts continuous measurement.

        .. note:: This command is only available in idle mode.
        """
        return self.execute(Svm41I2cCmdStartMeasurement())

    def stop_measurement(self):
        """
        Leaves the measurement mode and returns to the idle mode.

        .. note:: This command is only available in measurement mode.
        """
        return self.execute(Svm41I2cCmdStopMeasurement())

    def read_measured_values(self):
        """
        Returns the new measurement results.

        .. note:: This command is only available in measurement mode. The
                  firmware updates the measurement values every second. Polling
                  data with a faster sampling rate will return the same values.
                  The first measurement is available 1 second after the start
                  measurement command is issued. Any readout prior to this will
                  return zero initialized values.

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
        """  # noqa: E501
        return self.execute(Svm41I2cCmdReadMeasuredValues())

    def read_measured_values_raw(self):
        """
        Returns the new measurement results with raw values added.

        .. note:: This command is only available in measurement mode. The
                  firmware updates the measurement values every second. Polling
                  data with a faster sampling rate will return the same values.
                  The first measurement is available 1 second after the start
                  measurement command is issued. Any readout prior to this will
                  return zero initialized values.

        :return:
            The measured air quality, humidity and temperature including the
            raw values without algorithm compensation.

            - raw_humidity (:py:class:`~sensirion_i2c_svm41.response_types.Humidity`) -
              Humidity response object.
            - raw_temperature (:py:class:`~sensirion_i2c_svm41.response_types.Temperature`) -
              Temperature response object.
            - raw_voc_ticks (int) -
              Raw VOC output ticks as read from the SGP sensor.
            - raw_nox_ticks (int) -
              Raw NOx output ticks as read from the SGP sensor.
        :rtype:
            tuple
        """  # noqa: E501
        return self.execute(Svm41I2cCmdReadMeasuredValuesRaw())
