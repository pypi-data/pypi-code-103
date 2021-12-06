import datetime
import functools
import logging
import time

import numpy
from PySide2 import QtGui, QtWidgets

import asphodel
import hyperborea.proxy
from asphodel.streamutil import stream_fixed_duration
from asphodel.streamutil import filter_channel_data
from asphodel.streamutil import unpack_streaming_data

from .ui_hardware_tests import Ui_HardwareTestDialog

logger = logging.getLogger(__name__)


def bridge_test(device, stream_id, stream, channel_id, channel):
    bridge_count = device.get_strain_bridge_count(channel)

    def get_mean_value(subchannel_index):
        device_data = stream_fixed_duration(device, stream_ids=[stream_id],
                                            duration=0.1)
        channel_data = filter_channel_data(device_data, stream_id, channel_id)
        _indexes, unpacked_data = unpack_streaming_data(channel_data['data'])
        mean = numpy.nanmean(unpacked_data, axis=0)[subchannel_index]

        decoder = channel_data['channel_decoder']
        subchannel_name = decoder.subchannel_names[subchannel_index]

        return mean, subchannel_name

    device.warm_up_stream(stream_id, True)

    time.sleep(0.1)

    results = []

    try:
        for bridge_index in range(bridge_count):
            subchannel_index = device.get_strain_bridge_subchannel(
                channel, bridge_index)

            device.set_strain_outputs(channel_id, bridge_index, 1, 0)
            pos_mean, subchannel_name = get_mean_value(subchannel_index)

            device.set_strain_outputs(channel_id, bridge_index, 0, 1)
            neg_mean, _n = get_mean_value(subchannel_index)

            device.set_strain_outputs(channel_id, bridge_index, 0, 0)
            zero_mean, _n = get_mean_value(subchannel_index)

            r = device.check_strain_resistances(channel, bridge_index,
                                                zero_mean, pos_mean, neg_mean)

            values = device.get_strain_bridge_values(channel, bridge_index)

            results.append((r, subchannel_name, values))
    finally:
        device.warm_up_stream(stream_id, False)

    return results


def accel_test(device, stream_id, stream, channel_id, channel):
    def get_mean_value():
        # make sure the duration is enough to get at least a couple packets
        duration = max(2 / stream.rate, 0.1)
        device_data = stream_fixed_duration(device, stream_ids=[stream_id],
                                            duration=duration)
        channel_data = filter_channel_data(device_data, stream_id, channel_id)
        _indexes, unpacked_data = unpack_streaming_data(channel_data['data'])
        mean = numpy.nanmean(unpacked_data, axis=0)

        return mean[0:3]  # accel data occupies first 3 indexes

    device.warm_up_stream(stream_id, True)

    time.sleep(0.1)

    try:
        device.enable_accel_self_test(channel_id, True)
        enabled_mean = get_mean_value()

        device.enable_accel_self_test(channel_id, False)
        disabled_mean = get_mean_value()
    finally:
        device.warm_up_stream(stream_id, False)

    return (device.check_accel_self_test(channel, disabled_mean, enabled_mean),
            enabled_mean, disabled_mean)


def last_test(device):
    return True  # success


class HardwareTestDialog(QtWidgets.QDialog, Ui_HardwareTestDialog):
    def __init__(self, device_info, proxy, parent=None):
        super().__init__(parent)

        self.device_info = device_info
        self.proxy = proxy

        self.failures = 0
        self.tests = []  # list of DeviceOperations
        self.create_test_list()

        self.setupUi(self)

        self.test_log = ""
        self.testOutput.setPlainText(self.test_log)

        self.rerunButton = self.buttonBox.button(
            QtWidgets.QDialogButtonBox.Reset)
        self.rerunButton.setText(self.tr("Rerun Tests"))
        self.rerunButton.clicked.connect(self.start_tests)

        self.font = QtGui.QFontDatabase.systemFont(
            QtGui.QFontDatabase.FixedFont)
        self.testOutput.setFont(self.font)

    def create_test_list(self):
        for i, (name, supply_info) in enumerate(self.device_info['supplies']):
            check_supply_op = hyperborea.proxy.SimpleDeviceOperation(
                "check_supply", i)
            cb = functools.partial(self.supply_check_finished, name,
                                   supply_info)
            check_supply_op.completed.connect(cb)
            check_supply_op.error.connect(cb)
            self.tests.append(check_supply_op)

        for stream_id, stream in enumerate(self.device_info['streams']):
            channel_indexes = stream.channel_index_list[0:stream.channel_count]
            for channel_id in channel_indexes:
                if channel_id < len(self.device_info['channels']):
                    channel = self.device_info['channels'][channel_id]
                    ch_type = channel.channel_type
                    if (ch_type == asphodel.CHANNEL_TYPE_SLOW_ACCEL or
                            ch_type == asphodel.CHANNEL_TYPE_PACKED_ACCEL or
                            ch_type == asphodel.CHANNEL_TYPE_LINEAR_ACCEL):
                        self.tests.append(self.create_accel_test_op(
                            stream_id, stream, channel_id, channel))
                    elif (ch_type == asphodel.CHANNEL_TYPE_SLOW_STRAIN or
                            ch_type == asphodel.CHANNEL_TYPE_FAST_STRAIN or
                            ch_type == asphodel.CHANNEL_TYPE_COMPOSITE_STRAIN):
                        self.tests.append(self.create_bridge_test_op(
                            stream_id, stream, channel_id, channel))

        last_test_op = hyperborea.proxy.DeviceOperation(last_test)
        last_test_op.completed.connect(self.last_test_cb)
        last_test_op.error.connect(self.last_test_cb)
        self.tests.append(last_test_op)

    def create_accel_test_op(self, stream_id, stream, channel_id, channel):
        test_op = hyperborea.proxy.DeviceOperation(
            accel_test, stream_id, stream, channel_id, channel)
        cb = functools.partial(self.accel_test_finished, stream_id, stream,
                               channel_id, channel)
        test_op.completed.connect(cb)
        test_op.error.connect(cb)
        return test_op

    def accel_test_finished(self, stream_id, stream, channel_id, channel,
                            result=None):
        name = channel.name.decode("utf-8")
        if result is None:
            self.test_result(False, "{} bridge check aborted!".format(name))
        else:
            success = result[0]
            passfail = "pass" if success else "FAIL"
            self.test_result(result, "{} self test: {}".format(name, passfail))

    def create_bridge_test_op(self, stream_id, stream, channel_id, channel):
        test_op = hyperborea.proxy.DeviceOperation(
            bridge_test, stream_id, stream, channel_id, channel)
        cb = functools.partial(self.bridge_test_finished, stream_id, stream,
                               channel_id, channel)
        test_op.completed.connect(cb)
        test_op.error.connect(cb)
        return test_op

    def bridge_test_finished(self, stream_id, stream, channel_id, channel,
                             results=None):
        if results is None:
            name = channel.name.decode("utf-8")
            self.test_result(False, "{} bridge check aborted!".format(name))
        else:
            for r, subchannel_name, values in results:
                passed, pos_res, neg_res = r
                passfail = "pass" if passed else "FAIL"
                s = "{} resistances: pos={} ({:.0%}), neg={} ({:.0%}), {}"
                self.test_result(passed, s.format(
                    subchannel_name, round(pos_res), pos_res / values.nominal,
                    round(neg_res), neg_res / values.nominal, passfail))

    def start_tests(self):
        self.rerunButton.setEnabled(False)
        self.failures = 0
        for test_op in self.tests:
            self.proxy.send_job(test_op)

        # use ISO 8601 representation
        dt_str = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        start_message = "*** Start of tests {} ***\n\n".format(dt_str)
        self.test_log += start_message
        self.testOutput.setPlainText(self.test_log)

    def last_test_cb(self, success=False):
        self.rerunButton.setEnabled(True)

        if not success:
            self.test_log += "\nTests aborted!\n"

        plural = "failures" if self.failures != 1 else "failure"
        self.test_log += "\n{} {}\n\n".format(self.failures, plural)

        # use ISO 8601 representation
        dt_str = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        end_message = "*** End of tests {} ***\n\n".format(dt_str)
        self.test_log += end_message
        self.testOutput.setPlainText(self.test_log)

    def test_result(self, success, message):
        if not success:
            self.failures += 1

        self.test_log += message + "\n"
        self.testOutput.setPlainText(self.test_log)

    def supply_check_finished(self, name, info, result=None):
        if result is None:
            self.test_result(False, "{} check aborted!".format(name))
        else:
            value, result_flags = result
            scaled_value = value * info.scale + info.offset
            scaled_nominal = info.nominal * info.scale + info.offset
            if scaled_nominal != 0.0:
                percent = (scaled_value) / scaled_nominal * 100.0
            else:
                percent = 0.0
            formatted = asphodel.format_value_ascii(info.unit_type, info.scale,
                                                    scaled_value)

            success = True if result_flags == 0 else False
            passfail = "pass" if success else "FAIL"

            message = "{}: {} ({:.0f}%), result=0x{:02x}, {}".format(
                name, formatted, percent, result_flags, passfail)

            self.test_result(success, message)
