import logging
import os
import struct

from PySide2 import QtCore, QtGui, QtWidgets

import asphodel

from .ui_info_dialog import Ui_InfoDialog

logger = logging.getLogger(__name__)


class InfoDialog(QtWidgets.QDialog, Ui_InfoDialog):
    def __init__(self, device_info, parent=None):
        super().__init__(parent)

        self.device_info = device_info

        self.setupUi(self)

        self.font = QtGui.QFontDatabase.systemFont(
            QtGui.QFontDatabase.FixedFont)
        self.plainTextEdit.setFont(self.font)

        self.device_info_str = self.create_device_info_string()
        self.plainTextEdit.setPlainText(self.device_info_str)

        self.saveButton.clicked.connect(self.save)

    def create_device_info_string(self):
        d = self.device_info
        s = ""

        s += "Serial Number: {}\n".format(d['serial_number'])
        s += "User Tag 1: {}\n".format(d['user_tag_1'])
        s += "User Tag 2: {}\n".format(d['user_tag_2'])
        s += "Location String: {}\n".format(d['location_string'])
        s += "Max Outgoing Param Len: {}\n".format(
            d['max_outgoing_param_length'])
        s += "Max Incoming Param Len: {}\n".format(
            d['max_incoming_param_length'])
        s += "Stream Packet Length: {}\n".format(d['stream_packet_length'])
        s += "Protocol Version: {}\n".format(d['protocol_version'])
        s += "Board Info: {} rev {}\n".format(*d['board_info'])
        s += "Build Info: {}\n".format(d['build_info'])
        s += "Build Date: {}\n".format(d['build_date'])

        commit_id = d['commit_id'] if d['commit_id'] else "N/A"
        s += "Commit ID: {}\n".format(commit_id)
        repo_branch = d['repo_branch'] if d['repo_branch'] else "N/A"
        s += "Repo Branch: {}\n".format(repo_branch)
        repo_name = d['repo_name'] if d['repo_name'] else "N/A"
        s += "Repo Name: {}\n".format(repo_name)

        s += "Chip Family: {}\n".format(d['chip_family'])
        s += "Chip Model: {}\n".format(d['chip_model'])
        s += "Chip ID: {}\n".format(d['chip_id'])
        s += "Tag Locations: {}\n".format(
            ", ".join(map(lambda x: str(tuple(x)), d['tag_locations'])))

        if d['nvm_modified'] is True:
            nvm_modified = "Yes"
        elif d['nvm_modified'] is False:
            nvm_modified = "No"
        else:
            nvm_modified = "Unknown"
        s += "NVM Modified: {}\n".format(nvm_modified)

        nvm_hash = d['nvm_hash'] if d['nvm_hash'] else "N/A"
        s += "NVM Hash: {}\n".format(nvm_hash)
        setting_hash = d['setting_hash'] if d['setting_hash'] else "N/A"
        s += "Setting Hash: {}\n".format(setting_hash)

        s += "Bootloader Info: {}\n".format(d['bootloader_info'])
        s += "\n"
        s += "Library Protocol Version: {}\n".format(
            d['library_protocol_version'])
        s += "Library Build Info: {}\n".format(d['library_build_info'])
        s += "Library Build Date: {}\n".format(d['library_build_date'])
        s += "\n"
        s += "Stream Filler Bits: {}\n".format(d['stream_filler_bits'])
        s += "Stream ID Bits: {}\n".format(d['stream_id_bits'])
        s += "\n"
        s += "Streams\n"

        for i, stream in enumerate(d['streams']):
            s += "  Stream {}\n".format(i)
            channels = stream.channel_index_list[:stream.channel_count]
            s += "    channels: [{}]\n".format(", ".join(map(str, channels)))
            s += "    filler_bits={}, counter_bits={}\n".format(
                stream.filler_bits, stream.counter_bits)
            s += "    rate={:g}, rate_error={:g}%\n".format(
                stream.rate, stream.rate_error * 100.0)
            s += "    warm_up_delay={:g}\n".format(stream.warm_up_delay)
            rate_info = d['stream_rate_info'][i]
            if rate_info is None or not rate_info.available:
                s += "    no rate channel\n"
            else:
                s += "    rate_channel={}, rate_invert={}\n".format(
                    rate_info.channel_index, rate_info.invert)
                s += "    rate_scale={}, rate_offset={}\n".format(
                    rate_info.scale, rate_info.offset)

        s += "\n"
        s += "Channels\n"

        for i, channel in enumerate(d['channels']):
            s += "  Channel {}\n".format(i)
            s += "    name: {}\n".format(channel.name.decode("utf-8"))

            stream_ids = []
            for stream_id, stream in enumerate(d['streams']):
                channels = stream.channel_index_list[:stream.channel_count]
                if i in channels:
                    stream_ids.append(stream_id)
            if len(stream_ids) == 1:
                stream_id = stream_ids[0]
                s += "    stream: {}\n".format(stream_id)
                sampling_rate = d['streams'][stream_id].rate * channel.samples
                s += "    rate={:g}\n".format(sampling_rate)
            elif len(stream_ids) == 0:
                s += "    stream: None\n"
            else:
                s += "    streams: [{}]\n".format(
                    ", ".join(map(str, stream_ids)))

            try:
                t_str = asphodel.channel_type_names[channel.channel_type]
                channel_type_str = "{} ({})" .format(channel.channel_type,
                                                     t_str)
            except IndexError:
                channel_type_str = str(channel.channel_type)
            s += "    channel_type={}\n".format(channel_type_str)

            try:
                t_str = asphodel.unit_type_names[channel.unit_type]
                unit_type_str = "{} ({})" .format(channel.unit_type, t_str)
            except IndexError:
                unit_type_str = str(channel.unit_type)
            s += "    unit_type={}\n".format(unit_type_str)

            s += "    filler_bits={}, data_bits={}\n".format(
                channel.filler_bits, channel.data_bits)
            s += "    samples={}, bits_per_sample={}\n".format(
                channel.samples, channel.bits_per_sample)
            s += "    minimum={:g}, maximum={:g}, resolution={:g}\n".format(
                channel.minimum, channel.maximum, channel.resolution)
            coefficients = channel.coefficients[:channel.coefficients_length]
            coefficients_str = ", ".join(map("{:g}".format, coefficients))
            s += "    coefficients: [{}]\n".format(coefficients_str)
            s += "    Chunk Count: {}\n".format(channel.chunk_count)
            for chunk_id in range(channel.chunk_count):
                chunk_len = channel.chunk_lengths[chunk_id]
                chunk = channel.chunks[chunk_id][:chunk_len]
                chunk_str = ",".join(map("{:02x}".format, chunk))
                s += "      Chunk {}: [{}]\n".format(chunk_id, chunk_str)

        s += "\n"
        s += "Supplies\n"

        for i, (name, supply) in enumerate(d['supplies']):
            s += "  Supply {}\n".format(i)
            s += "    name: {}\n".format(name)

            try:
                t_str = asphodel.unit_type_names[supply.unit_type]
                unit_type_str = "{} ({})" .format(supply.unit_type, t_str)
            except IndexError:
                unit_type_str = str(supply.unit_type)
            s += "    unit_type={}\n".format(unit_type_str)
            s += "    is_battery={}, nominal={}\n".format(supply.is_battery,
                                                          supply.nominal)
            s += "    scale={:g}, offset={:g}\n".format(supply.scale,
                                                        supply.offset)

            supply_results = d['supply_results'][i]
            if supply_results is not None:
                value, result_flags = supply_results
                scaled_value = value * supply.scale + supply.offset
                scaled_nominal = supply.nominal * supply.scale + supply.offset
                if scaled_nominal != 0.0:
                    percent = (scaled_value) / scaled_nominal * 100.0
                else:
                    percent = 0.0
                formatted = asphodel.format_value_ascii(
                    supply.unit_type, supply.scale, scaled_value)
                passfail = "pass" if result_flags == 0 else "FAIL"
                s += "    value={}, result=0x{:02x} ({})\n".format(
                    value, result_flags, passfail)
                s += "    scaled_value={} ({:.0f}%)\n".format(
                    formatted, percent)
            else:
                s += "    value=Error\n"

        s += "\n"
        s += "Control Variables\n"

        for i, (name, ctrl_var, _setting) in enumerate(d['ctrl_vars']):
            s += "  Control Variable {}\n".format(i)
            s += "    name: {}\n".format(name)

            try:
                t_str = asphodel.unit_type_names[ctrl_var.unit_type]
                unit_type_str = "{} ({})" .format(ctrl_var.unit_type, t_str)
            except IndexError:
                unit_type_str = str(ctrl_var.unit_type)
            s += "    unit_type={}\n".format(unit_type_str)
            s += "    minimum={}, maximum={}\n".format(ctrl_var.minimum,
                                                       ctrl_var.maximum)
            s += "    scale={:g}, offset={:g}\n".format(ctrl_var.scale,
                                                        ctrl_var.offset)

        s += "\n"
        s += "Settings\n"
        for setting_id, setting in enumerate(d['settings']):
            s += self.get_setting_string(setting_id, setting)

        s += "\n"
        s += "NVM\n"

        s += "\n".join(asphodel.format_nvm_data(d['nvm']))

        return s

    def get_setting_string(self, setting_id, setting):
        lines = []
        lines.append(f"  Setting {setting_id}")
        setting_name = setting.name.decode("UTF-8")
        lines.append(f"    name: {setting_name}")

        try:
            t = asphodel.setting_type_names[setting.setting_type]
        except IndexError:
            t = None

        length = setting.default_bytes_length
        default_bytes = bytes(setting.default_bytes[0:length])

        if t == "SETTING_TYPE_BYTE":
            s = setting.u.byte_setting
            if len(default_bytes) == 1:
                lines.append("    default={}".format(default_bytes[0]))
            else:
                lines.append("    default=<ERROR>")
            byte_offset = s.nvm_word * 4 + s.nvm_word_byte
            value = struct.unpack_from(">B", self.device_info['nvm'],
                                       byte_offset)[0]
            lines.append("    value={}".format(value))
        elif t == "SETTING_TYPE_BOOLEAN":
            s = setting.u.byte_setting
            if len(default_bytes) == 1:
                lines.append("    default={}".format(bool(default_bytes[0])))
            else:
                lines.append("    default=<ERROR>")
            byte_offset = s.nvm_word * 4 + s.nvm_word_byte
            value = struct.unpack_from(">?", self.device_info['nvm'],
                                       byte_offset)[0]
            lines.append("    value={}".format(value))
        elif t == "SETTING_TYPE_UNIT_TYPE":
            s = setting.u.byte_setting
            if len(default_bytes) == 1:
                try:
                    n = asphodel.unit_type_names[default_bytes[0]]
                    unit_type_str = "{} ({})" .format(default_bytes[0], n)
                except IndexError:
                    unit_type_str = str(default_bytes[0])
                lines.append("    default={}".format(unit_type_str))
            else:
                lines.append("    default=<ERROR>")
            byte_offset = s.nvm_word * 4 + s.nvm_word_byte
            value = struct.unpack_from(">B", self.device_info['nvm'],
                                       byte_offset)[0]
            try:
                n = asphodel.unit_type_names[value]
                unit_type_str = "{} ({})" .format(value, n)
            except IndexError:
                unit_type_str = str(value)
            lines.append("    value={}".format(unit_type_str))
        elif t == "SETTING_TYPE_CHANNEL_TYPE":
            s = setting.u.byte_setting
            if len(default_bytes) == 1:
                try:
                    n = asphodel.channel_type_names[default_bytes[0]]
                    channel_type_str = "{} ({})" .format(default_bytes[0], n)
                except IndexError:
                    channel_type_str = str(default_bytes[0])
                lines.append("    default={}".format(channel_type_str))
            else:
                lines.append("    default=<ERROR>")
            byte_offset = s.nvm_word * 4 + s.nvm_word_byte
            value = struct.unpack_from(">B", self.device_info['nvm'],
                                       byte_offset)[0]
            try:
                n = asphodel.channel_type_names[value]
                channel_type_str = "{} ({})" .format(value, n)
            except IndexError:
                channel_type_str = str(value)
            lines.append("    value={}".format(channel_type_str))
        elif t == "SETTING_TYPE_BYTE_ARRAY":
            s = setting.u.byte_array_setting
            default_str = ",".join(map("{:02x}".format, default_bytes))
            lines.append("    default=[{}]".format(default_str))
            length_byte_offset = s.length_nvm_word * 4 + s.length_nvm_word_byte
            length = struct.unpack_from(">B", self.device_info['nvm'],
                                        length_byte_offset)[0]
            if length > s.maximum_length:
                length = s.maximum_length
            fmt = ">{}s".format(length)
            value = struct.unpack_from(fmt, self.device_info['nvm'],
                                       s.nvm_word * 4)[0]
            value_str = ",".join(map("{:02x}".format, value))
            lines.append("    value={}".format(value_str))
        elif t == "SETTING_TYPE_STRING":
            s = setting.u.string_setting
            try:
                default_str = default_bytes.decode("UTF-8")
            except UnicodeDecodeError:
                default_str = "<ERROR>"
            lines.append("    default={}".format(default_str))
            fmt = ">{}s".format(s.maximum_length)
            raw = struct.unpack_from(fmt, self.device_info['nvm'],
                                     s.nvm_word * 4)[0]
            raw = raw.split(b'\x00', 1)[0]
            raw = raw.split(b'\xff', 1)[0]
            try:
                value = raw.decode("UTF-8")
            except UnicodeDecodeError:
                value = "<ERROR>"
            lines.append("    value={}".format(value))
        elif t == "SETTING_TYPE_INT32":
            s = setting.u.int32_setting
            if len(default_bytes) == 4:
                default = struct.unpack_from(">i", default_bytes, 0)[0]
                lines.append("    default={}".format(default))
            else:
                lines.append("    default=<ERROR>")
            value = struct.unpack_from(">i", self.device_info['nvm'],
                                       s.nvm_word * 4)[0]
            lines.append("    value={}".format(value))
        elif t == "SETTING_TYPE_INT32_SCALED":
            s = setting.u.int32_scaled_setting
            if len(default_bytes) == 4:
                default = struct.unpack_from(">i", default_bytes, 0)[0]
                scaled = default * s.scale + s.offset
                lines.append("    default={}".format(scaled))
            else:
                lines.append("    default=<ERROR>")
            try:
                n = asphodel.unit_type_names[s.unit_type]
                unit_type_str = "{} ({})" .format(s.unit_type, n)
            except IndexError:
                unit_type_str = str(s.unit_type)
            lines.append("    unit_type={}".format(unit_type_str))
            value = struct.unpack_from(">i", self.device_info['nvm'],
                                       s.nvm_word * 4)[0]
            scaled_value = value * s.scale + s.offset
            lines.append("    value={}".format(scaled_value))
        elif t == "SETTING_TYPE_FLOAT":
            s = setting.u.float_setting
            if len(default_bytes) == 4:
                default = struct.unpack_from(">f", default_bytes, 0)[0]
                scaled = default * s.scale + s.offset
                lines.append("    default={}".format(scaled))
            else:
                lines.append("    default=<ERROR>")
            try:
                n = asphodel.unit_type_names[s.unit_type]
                unit_type_str = "{} ({})" .format(s.unit_type, n)
            except IndexError:
                unit_type_str = str(s.unit_type)
            lines.append("    unit_type={}".format(unit_type_str))
            value = struct.unpack_from(">f", self.device_info['nvm'],
                                       s.nvm_word * 4)[0]
            scaled_value = value * s.scale + s.offset
            lines.append("    value={}".format(scaled_value))
        elif t == "SETTING_TYPE_FLOAT_ARRAY":
            s = setting.u.float_array_setting

            if len(default_bytes) % 4 == 0:
                fmt = ">{}f".format(len(default_bytes) // 4)
                values = struct.unpack_from(fmt, default_bytes, 0)
                scaled_values = [f * s.scale + s.offset for f in values]
                values_str = ", ".join(map(str, values))
                scaled_values_str = ", ".join(map(str, scaled_values))
                lines.append("    default=[{}]".format(scaled_values_str))
            else:
                lines.append("    default=<ERROR>")

            try:
                n = asphodel.unit_type_names[s.unit_type]
                unit_type_str = "{} ({})" .format(s.unit_type, n)
            except IndexError:
                unit_type_str = str(s.unit_type)
            lines.append("    unit_type={}".format(unit_type_str))
            length_byte_offset = s.length_nvm_word * 4 + s.length_nvm_word_byte
            length = struct.unpack_from(">B", self.device_info['nvm'],
                                        length_byte_offset)[0]
            if length > s.maximum_length:
                length = s.maximum_length
            fmt = ">{}f".format(length)
            values = struct.unpack_from(fmt, self.device_info['nvm'],
                                        s.nvm_word * 4)
            scaled_values = [f * s.scale + s.offset for f in values]
            values_str = ", ".join(map(str, values))
            scaled_values_str = ", ".join(map(str, scaled_values))
            lines.append("    values=[{}]".format(values_str))
            lines.append("    scaled_values=[{}]".format(scaled_values_str))
        elif t == "SETTING_TYPE_CUSTOM_ENUM":
            s = setting.u.custom_enum_setting
            try:
                enum = self.device_info['custom_enums'][s.custom_enum_index]
            except KeyError:
                enum = []

            if len(default_bytes) == 1:
                default_value = default_bytes[0]
                try:
                    default_str = enum[default_value]
                except IndexError:
                    default_str = "unknown ({})".format(default_value)
            else:
                default_str = "<ERROR>"
            lines.append("    default={}".format(default_str))
            byte_offset = s.nvm_word * 4 + s.nvm_word_byte
            value = struct.unpack_from(">B", self.device_info['nvm'],
                                       byte_offset)[0]

            try:
                value_str = enum[value]
            except IndexError:
                value_str = "unknown ({})".format(value)
            lines.append("    value={}".format(value_str))
        else:
            lines.append("    unknown setting type!")

        lines.append("")  # to add trailing "\n"
        return "\n".join(lines)

    def get_save_path(self):
        serial_number = self.device_info['serial_number']
        default_name = f"{serial_number}.txt"

        # find the directory from settings
        settings = QtCore.QSettings()
        directory = settings.value("infoSaveDirectory")
        if directory and type(directory) == str:
            if not os.path.isdir(directory):
                directory = None

        if not directory:
            directory = QtCore.QStandardPaths.writableLocation(
                QtCore.QStandardPaths.DocumentsLocation)

        file_and_dir = os.path.join(directory, default_name)

        caption = self.tr("Save Device Information")
        file_filter = self.tr("Text Files (*.txt);;All Files (*.*)")
        val = QtWidgets.QFileDialog.getSaveFileName(
            self, caption, file_and_dir, file_filter)
        output_path = val[0]

        if output_path:
            # save the directory
            output_dir = os.path.dirname(output_path)
            settings.setValue("infoSaveDirectory", output_dir)
            return os.path.abspath(output_path)
        else:
            return None

    def save(self):
        path = self.get_save_path()
        if path:
            try:
                with open(path, "wt", encoding="utf-8") as f:
                    f.write(self.device_info_str)
                    f.write("\n")  # trailing newline
            except Exception:
                msg = f"Error writing file {path}."
                logger.exception(msg)
                QtWidgets.QMessageBox.critical(self, self.tr("Error"),
                                               self.tr(msg))
                return
