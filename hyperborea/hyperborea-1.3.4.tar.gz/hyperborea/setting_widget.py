import struct

from PySide2 import QtCore, QtGui, QtWidgets

import asphodel

from .unit_formatter_spinbox import UnitFormatterSpinBox
from .unit_formatter_spinbox import UnitFormatterDoubleSpinBox


class StringLengthValidator(QtGui.QValidator):
    def __init__(self, max_length, parent=None):
        super().__init__(parent)
        self.max_length = max_length

    def fixup(self, input_text):
        return input_text

    def validate(self, input_text, pos):
        try:
            utf_bytes = input_text.encode("UTF-8")
        except Exception:
            return (QtGui.QValidator.State.Invalid, input_text, pos)

        if len(utf_bytes) <= self.max_length:
            return (QtGui.QValidator.State.Acceptable, input_text, pos)
        else:
            return (QtGui.QValidator.State.Invalid, input_text, pos)


class SettingWidget(QtWidgets.QWidget):
    def __init__(self, setting, nvm_bytes, custom_enums, parent=None):
        super().__init__(parent)

        self.setting = setting
        self.nvm_bytes = nvm_bytes
        self.custom_enums = custom_enums

        if self.setting is not None:
            length = self.setting.default_bytes_length
            self.default_bytes = bytes(self.setting.default_bytes[0:length])

        if self.setting is None:
            self.setup_unknown_setting_type()
        elif self.setting.setting_type == asphodel.SETTING_TYPE_BYTE:
            self.setup_byte()
        elif self.setting.setting_type == asphodel.SETTING_TYPE_BOOLEAN:
            self.setup_boolean()
        elif self.setting.setting_type == asphodel.SETTING_TYPE_UNIT_TYPE:
            self.setup_unit_type()
        elif self.setting.setting_type == asphodel.SETTING_TYPE_CHANNEL_TYPE:
            self.setup_channel_type()
        elif self.setting.setting_type == asphodel.SETTING_TYPE_BYTE_ARRAY:
            self.setup_byte_array()
        elif self.setting.setting_type == asphodel.SETTING_TYPE_STRING:
            self.setup_string()
        elif self.setting.setting_type == asphodel.SETTING_TYPE_INT32:
            self.setup_int32()
        elif self.setting.setting_type == asphodel.SETTING_TYPE_INT32_SCALED:
            self.setup_int32_scaled()
        elif self.setting.setting_type == asphodel.SETTING_TYPE_FLOAT:
            self.setup_float()
        elif self.setting.setting_type == asphodel.SETTING_TYPE_FLOAT_ARRAY:
            self.setup_float_array()
        elif self.setting.setting_type == asphodel.SETTING_TYPE_CUSTOM_ENUM:
            self.setup_custom_enum()
        else:
            self.setup_unknown_setting_type()

    def restore_defaults(self):
        pass  # this function is likely to be overridden

    def create_setting_label(self):
        # this is used by most setting types, so do it here
        setting_name = self.setting.name.decode("UTF-8")
        setting_label = QtWidgets.QLabel(self)
        setting_label.setText(setting_name)

        return setting_label

    def setup_unknown_setting_type(self):
        self.setting_label = self.create_setting_label()

        self.unknown_label = QtWidgets.QLabel(self)
        self.unknown_label.setText("Unknown Setting Type!")

        style = "QLabel { font-weight: bold; color : red; }"
        self.unknown_label.setStyleSheet(style)

        def update_nvm(nvm_bytes):
            pass  # don't know how

        self.update_nvm = update_nvm
        self.widgets = (self.setting_label, self.unknown_label)

    def setup_byte(self):
        s = self.setting.u.byte_setting

        self.setting_label = self.create_setting_label()

        self.spinbox = QtWidgets.QSpinBox(self)

        byte_offset = s.nvm_word * 4 + s.nvm_word_byte
        initial = struct.unpack_from(">B", self.nvm_bytes, byte_offset)[0]

        self.spinbox.setMinimum(0)
        self.spinbox.setMaximum(255)
        self.spinbox.setValue(initial)

        # determine the default value
        if len(self.default_bytes) == 1:
            default_value = self.default_bytes[0]
            default_str = "{}".format(default_value)

            def restore_defaults():
                self.spinbox.setValue(default_value)
            self.restore_defaults = restore_defaults
        else:
            default_str = "unknown"
        tool_tip_str = "default: {}".format(default_str)
        self.setting_label.setToolTip(tool_tip_str)
        self.spinbox.setToolTip(tool_tip_str)

        def update_nvm(nvm_bytes):
            value = self.spinbox.value()
            struct.pack_into(">B", nvm_bytes, byte_offset, value)

        self.update_nvm = update_nvm
        self.widgets = (self.setting_label, self.spinbox)

    def setup_boolean(self):
        s = self.setting.u.byte_setting

        self.check_box = QtWidgets.QCheckBox(self)

        setting_name = self.setting.name.decode("UTF-8")
        self.check_box.setText(setting_name)

        byte_offset = s.nvm_word * 4 + s.nvm_word_byte
        initial = struct.unpack_from(">?", self.nvm_bytes, byte_offset)[0]

        self.check_box.setChecked(initial)

        # determine the default value
        if len(self.default_bytes) == 1:
            default_value = bool(self.default_bytes[0])
            default_str = "{}".format(default_value)

            def restore_defaults():
                self.check_box.setChecked(default_value)
            self.restore_defaults = restore_defaults
        else:
            default_str = "unknown"
        tool_tip_str = "default: {}".format(default_str)
        self.check_box.setToolTip(tool_tip_str)

        def update_nvm(nvm_bytes):
            new_value = self.check_box.isChecked()
            struct.pack_into(">?", nvm_bytes, byte_offset, new_value)

        self.update_nvm = update_nvm
        self.widgets = (self.check_box,)  # only one widget; span all columns

    def setup_unit_type(self):
        s = self.setting.u.byte_setting

        # determine the default value
        if len(self.default_bytes) == 1:
            default_str = "{}".format(self.default_bytes[0])
        else:
            default_str = "unknown"

        self.setting_label = self.create_setting_label()

        option_values = []

        self.combo_box = QtWidgets.QComboBox(self)

        for i, name in enumerate(asphodel.unit_type_names):
            value = getattr(asphodel, name)
            option_values.append(value)
            self.combo_box.insertItem(i, name)

        byte_offset = s.nvm_word * 4 + s.nvm_word_byte
        initial = struct.unpack_from(">B", self.nvm_bytes, byte_offset)[0]

        try:
            initial_index = option_values.index(initial)
        except ValueError:
            initial_index = len(option_values)
            option_values.append(initial)
            error_item_str = "unknown ({})".format(initial)
            self.combo_box.insertItem(initial_index, error_item_str)

        self.combo_box.setCurrentIndex(initial_index)

        # determine the default value
        if len(self.default_bytes) == 1:
            default_value = self.default_bytes[0]
            try:
                default_index = option_values.index(default_value)
                default_str = asphodel.unit_type_names[default_value]
            except ValueError:
                default_index = len(option_values)
                option_values.append(default_value)
                default_str = "unknown ({})".format(default_value)
                self.combo_box.insertItem(default_index, default_str)
            except IndexError:
                # default str wasn't set
                default_str = error_item_str

            def restore_defaults():
                self.combo_box.setCurrentIndex(default_index)
            self.restore_defaults = restore_defaults
        else:
            default_str = "unknown"
        tool_tip_str = "default: {}".format(default_str)
        self.setting_label.setToolTip(tool_tip_str)
        self.combo_box.setToolTip(tool_tip_str)

        def update_nvm(nvm_bytes):
            index = self.combo_box.currentIndex()
            new_value = option_values[index]
            struct.pack_into(">B", nvm_bytes, byte_offset, new_value)

        self.update_nvm = update_nvm
        self.widgets = (self.setting_label, self.combo_box)

    def setup_channel_type(self):
        s = self.setting.u.byte_setting

        self.setting_label = self.create_setting_label()

        option_values = []

        self.combo_box = QtWidgets.QComboBox(self)

        for i, name in enumerate(asphodel.channel_type_names):
            value = getattr(asphodel, name)
            option_values.append(value)
            self.combo_box.insertItem(i, name)

        byte_offset = s.nvm_word * 4 + s.nvm_word_byte
        initial = struct.unpack_from(">B", self.nvm_bytes, byte_offset)[0]

        try:
            initial_index = option_values.index(initial)
        except ValueError:
            initial_index = len(option_values)
            option_values.append(initial)
            error_item_str = "unknown ({})".format(initial)
            self.combo_box.insertItem(initial_index, error_item_str)

        self.combo_box.setCurrentIndex(initial_index)

        # determine the default value
        if len(self.default_bytes) == 1:
            default_value = self.default_bytes[0]
            try:
                default_index = option_values.index(default_value)
                default_str = asphodel.channel_type_names[default_value]
            except ValueError:
                default_index = len(option_values)
                option_values.append(default_value)
                default_str = "unknown ({})".format(default_value)
                self.combo_box.insertItem(default_index, default_str)
            except IndexError:
                # default str wasn't set
                default_str = error_item_str

            def restore_defaults():
                self.combo_box.setCurrentIndex(default_index)
            self.restore_defaults = restore_defaults
        else:
            default_str = "unknown"
        tool_tip_str = "default: {}".format(default_str)
        self.setting_label.setToolTip(tool_tip_str)
        self.combo_box.setToolTip(tool_tip_str)

        def update_nvm(nvm_bytes):
            index = self.combo_box.currentIndex()
            new_value = option_values[index]
            struct.pack_into(">B", nvm_bytes, byte_offset, new_value)

        self.update_nvm = update_nvm
        self.widgets = (self.setting_label, self.combo_box)

    def setup_byte_array(self):
        s = self.setting.u.byte_array_setting

        self.setting_label = self.create_setting_label()

        self.lineedit = QtWidgets.QLineEdit(self)
        self.regexp = QtCore.QRegExp("[1-9, ]?")
        self.validator = QtGui.QRegExpValidator(self.regexp, self)
        self.lineedit.setValidator(self.validator)

        len_offset = s.length_nvm_word * 4 + s.length_nvm_word_byte
        initial_len = struct.unpack_from(">B", self.nvm_bytes, len_offset)[0]
        initial_len = min(initial_len, s.maxiumum_length)

        fmt = ">{}B".format(initial_len)
        initial_array = struct.unpack_from(fmt, self.nvm_bytes, s.nvm_word * 4)
        initial_str = ", ".join(map(str, initial_array))

        self.lineedit.setText(initial_str)

        # determine the default value
        default_str = ", ".join(map(str, self.default_bytes))

        def restore_defaults():
            self.lineedit.setText(default_str)
        self.restore_defaults = restore_defaults
        tool_tip_str = "default: [{}]".format(default_str)
        self.setting_label.setToolTip(tool_tip_str)
        self.lineedit.setToolTip(tool_tip_str)

        def update_nvm(nvm_bytes):
            text = self.lineedit.text()
            if text.strip():
                array = list(map(int, text.split(",")))
            else:
                array = []
            struct.pack_into(">B", nvm_bytes, len_offset, len(array))
            fmt = ">{}B".format(len(array))
            struct.pack_into(fmt, nvm_bytes, s.nvm_word * 4, array)

        self.update_nvm = update_nvm
        self.widgets = (self.setting_label, self.lineedit)

    def setup_string(self):
        s = self.setting.u.string_setting

        self.setting_label = self.create_setting_label()

        self.lineedit = QtWidgets.QLineEdit(self)
        self.validator = StringLengthValidator(s.maximum_length, self)
        self.lineedit.setValidator(self.validator)

        fmt = ">{}s".format(s.maximum_length)
        raw = struct.unpack_from(fmt, self.nvm_bytes, s.nvm_word * 4)[0]
        raw = raw.split(b'\x00', 1)[0]
        raw = raw.split(b'\xff', 1)[0]

        try:
            value = raw.decode("UTF-8")
        except UnicodeDecodeError:
            value = "<ERROR>"

        self.lineedit.setText(value)

        # determine the default value
        try:
            default_str = self.default_bytes.decode("UTF-8")

            def restore_defaults():
                self.lineedit.setText(default_str)
            self.restore_defaults = restore_defaults
        except UnicodeDecodeError:
            default_str = "unknown"
        tool_tip_str = "default: {}".format(default_str)
        self.setting_label.setToolTip(tool_tip_str)
        self.lineedit.setToolTip(tool_tip_str)

        def update_nvm(nvm_bytes):
            text = self.lineedit.text()
            value = text.encode("UTF-8")
            struct.pack_into(fmt, nvm_bytes, s.nvm_word * 4, value)

        self.update_nvm = update_nvm
        self.widgets = (self.setting_label, self.lineedit)

    def setup_int32(self):
        s = self.setting.u.int32_setting

        self.setting_label = self.create_setting_label()

        self.spinbox = QtWidgets.QSpinBox(self)

        initial = struct.unpack_from(">i", self.nvm_bytes, s.nvm_word * 4)[0]

        self.spinbox.setMinimum(s.minimum)
        self.spinbox.setMaximum(s.maximum)
        self.spinbox.setValue(initial)

        # determine the default value
        if len(self.default_bytes) == 4:
            default_value = struct.unpack_from(">i", self.default_bytes, 0)[0]
            default_str = "{}".format(default_value)

            def restore_defaults():
                self.spinbox.setValue(default_value)
            self.restore_defaults = restore_defaults
        else:
            default_str = "unknown"
        tool_tip_str = "default: {}".format(default_str)
        self.setting_label.setToolTip(tool_tip_str)
        self.spinbox.setToolTip(tool_tip_str)

        def update_nvm(nvm_bytes):
            value = self.spinbox.value()
            struct.pack_into(">i", nvm_bytes, s.nvm_word * 4, value)

        self.update_nvm = update_nvm
        self.widgets = (self.setting_label, self.spinbox)

    def setup_int32_scaled(self):
        s = self.setting.u.int32_scaled_setting

        self.setting_label = self.create_setting_label()

        scaled_min = s.minimum * s.scale + s.offset
        scaled_max = s.maximum * s.scale + s.offset
        unit_formatter = asphodel.nativelib.create_unit_formatter(
            s.unit_type, scaled_min, scaled_max, s.scale)

        # update the unit formatter's scale and offset
        unit_formatter.conversion_offset += (s.offset *
                                             unit_formatter.conversion_scale)
        unit_formatter.conversion_scale *= s.scale

        if unit_formatter.conversion_scale < 0.0:
            inverted = True
            unit_formatter.conversion_scale = -unit_formatter.conversion_scale
        else:
            inverted = False

        self.spinbox = UnitFormatterSpinBox(unit_formatter, self)

        initial = struct.unpack_from(">i", self.nvm_bytes, s.nvm_word * 4)[0]

        if not inverted:
            self.spinbox.setMinimum(s.minimum)
            self.spinbox.setMaximum(s.maximum)
            self.spinbox.setValue(initial)
        else:
            # min and max are backwards
            self.spinbox.setMinimum(-s.maximum)
            self.spinbox.setMaximum(-s.minimum)
            self.spinbox.setValue(-initial)

        # determine the default value
        if len(self.default_bytes) == 4:
            default_value = struct.unpack_from(">i", self.default_bytes, 0)[0]

            scaled_value = (default_value * unit_formatter.conversion_scale +
                            unit_formatter.conversion_offset)
            default_str = unit_formatter.format_utf8(scaled_value)

            def restore_defaults():
                if not inverted:
                    self.spinbox.setValue(default_value)
                else:
                    self.spinbox.setValue(-default_value)
            self.restore_defaults = restore_defaults
        else:
            default_str = "unknown"
        tool_tip_str = "default: {}".format(default_str)
        self.setting_label.setToolTip(tool_tip_str)
        self.spinbox.setToolTip(tool_tip_str)

        def update_nvm(nvm_bytes):
            value = self.spinbox.value()
            if inverted:
                value = -value
            struct.pack_into(">i", nvm_bytes, s.nvm_word * 4, value)

        self.update_nvm = update_nvm
        self.widgets = (self.setting_label, self.spinbox)

    def setup_float(self):
        s = self.setting.u.float_setting

        self.setting_label = self.create_setting_label()

        scaled_min = s.minimum * s.scale + s.offset
        scaled_max = s.maximum * s.scale + s.offset
        unit_formatter = asphodel.nativelib.create_unit_formatter(
            s.unit_type, scaled_min, scaled_max, 0)

        # update the unit formatter's scale and offset
        unit_formatter.conversion_offset += (s.offset *
                                             unit_formatter.conversion_scale)
        unit_formatter.conversion_scale *= s.scale

        if unit_formatter.conversion_scale < 0.0:
            inverted = True
            unit_formatter.conversion_scale = -unit_formatter.conversion_scale
        else:
            inverted = False

        self.spinbox = UnitFormatterDoubleSpinBox(unit_formatter, self)

        initial = struct.unpack_from(">f", self.nvm_bytes, s.nvm_word * 4)[0]

        if not inverted:
            self.spinbox.setMinimum(s.minimum)
            self.spinbox.setMaximum(s.maximum)
            self.spinbox.setValue(initial)
        else:
            # min and max are backwards
            self.spinbox.setMinimum(-s.maximum)
            self.spinbox.setMaximum(-s.minimum)
            self.spinbox.setValue(-initial)

        # determine the default value
        if len(self.default_bytes) == 4:
            default_value = struct.unpack_from(">f", self.default_bytes, 0)[0]

            scaled_value = (default_value * unit_formatter.conversion_scale +
                            unit_formatter.conversion_offset)
            default_str = unit_formatter.format_utf8(scaled_value)

            def restore_defaults():
                if not inverted:
                    self.spinbox.setValue(default_value)
                else:
                    self.spinbox.setValue(-default_value)
            self.restore_defaults = restore_defaults
        else:
            default_str = "unknown"
        tool_tip_str = "default: {}".format(default_str)
        self.setting_label.setToolTip(tool_tip_str)
        self.spinbox.setToolTip(tool_tip_str)

        def update_nvm(nvm_bytes):
            value = self.spinbox.value()
            if inverted:
                value = -value
            struct.pack_into(">f", nvm_bytes, s.nvm_word * 4, value)

        self.update_nvm = update_nvm
        self.widgets = (self.setting_label, self.spinbox)

    def setup_float_array(self):
        s = self.setting.u.float_array_setting

        self.setting_label = self.create_setting_label()

        self.lineedit = QtWidgets.QLineEdit(self)
        self.regexp = QtCore.QRegExp("[1-9, .e\-]?")
        self.validator = QtGui.QRegExpValidator(self.regexp, self)
        self.lineedit.setValidator(self.validator)

        scaled_min = s.minimum * s.scale + s.offset
        scaled_max = s.maximum * s.scale + s.offset
        unit_formatter = asphodel.nativelib.create_unit_formatter(
            s.unit_type, scaled_min, scaled_max, 0)

        scale = unit_formatter.conversion_scale * s.scale
        offset = (unit_formatter.conversion_offset +
                  s.offset * unit_formatter.conversion_scale)

        self.unitlabel = QtWidgets.QLabel(self)
        self.unitlabel.setText(unit_formatter.unit_utf8)

        len_offset = s.length_nvm_word * 4 + s.length_nvm_word_byte
        initial_len = struct.unpack_from(">B", self.nvm_bytes, len_offset)[0]
        initial_len = min(initial_len, s.maxiumum_length)

        fmt = ">{}f".format(initial_len)
        initial_array = struct.unpack_from(fmt, self.nvm_bytes, s.nvm_word * 4)
        initial_array = [x * scale + offset for x in initial_array]
        initial_str = ", ".join(map(str, initial_array))

        self.lineedit.setText(initial_str)

        # determine the default value
        if len(self.default_bytes) % 4 == 0:
            fmt = ">{}f".format(len(self.default_bytes) // 4)
            default_array = struct.unpack_from(fmt, self.default_bytes, 0)
            default_array = [x * scale + offset for x in default_array]
            default_str = ", ".join(map(str, default_array))

            def restore_defaults():
                self.lineedit.setText(default_str)
            self.restore_defaults = restore_defaults
            tool_tip_str = "default: [{}]".format(default_str)
        else:
            tool_tip_str = "default: unknown"
        self.setting_label.setToolTip(tool_tip_str)
        self.lineedit.setToolTip(tool_tip_str)

        def update_nvm(nvm_bytes):
            text = self.lineedit.text()
            if text.strip():
                array = list(map(float, text.split(",")))
            else:
                array = []

            array = [(x - offset) / scale for x in array]
            array = [min(max(x, s.minimum), s.maximum) for x in array]

            struct.pack_into(">B", nvm_bytes, len_offset, len(array))
            fmt = ">{}f".format(len(array))
            struct.pack_into(fmt, nvm_bytes, s.nvm_word * 4, array)

        self.update_nvm = update_nvm
        # TODO: include unitlabel
        self.widgets = (self.setting_label, self.lineedit)

    def setup_custom_enum(self):
        s = self.setting.u.custom_enum_setting

        self.setting_label = self.create_setting_label()

        option_values = []

        self.combo_box = QtWidgets.QComboBox(self)

        for i, name in enumerate(self.custom_enums[s.custom_enum_index]):
            option_values.append(i)
            self.combo_box.insertItem(i, name)

        byte_offset = s.nvm_word * 4 + s.nvm_word_byte
        initial = struct.unpack_from(">B", self.nvm_bytes, byte_offset)[0]

        try:
            initial_index = option_values.index(initial)
        except ValueError:
            initial_index = len(option_values)
            option_values.append(initial)
            error_item_str = "unknown ({})".format(initial)
            self.combo_box.insertItem(initial_index, error_item_str)

        self.combo_box.setCurrentIndex(initial_index)

        # determine the default value
        if len(self.default_bytes) == 1:
            default_value = self.default_bytes[0]
            try:
                default_index = option_values.index(default_value)
                enum = self.custom_enums[s.custom_enum_index]
                default_str = enum[default_value]
            except ValueError:
                default_index = len(option_values)
                option_values.append(default_value)
                default_str = "unknown ({})".format(default_value)
                self.combo_box.insertItem(default_index, default_str)
            except IndexError:
                # default str wasn't set
                default_str = error_item_str

            def restore_defaults():
                self.combo_box.setCurrentIndex(default_index)
            self.restore_defaults = restore_defaults
        else:
            default_str = "unknown"
        tool_tip_str = "default: {}".format(default_str)
        self.setting_label.setToolTip(tool_tip_str)
        self.combo_box.setToolTip(tool_tip_str)

        def update_nvm(nvm_bytes):
            index = self.combo_box.currentIndex()
            new_value = option_values[index]
            struct.pack_into(">B", nvm_bytes, byte_offset, new_value)

        self.update_nvm = update_nvm
        self.widgets = (self.setting_label, self.combo_box)
