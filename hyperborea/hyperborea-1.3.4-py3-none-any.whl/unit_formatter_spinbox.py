import math

from PySide2 import QtGui, QtWidgets

import asphodel


class UnitFormatterSpinBox(QtWidgets.QSpinBox):
    def __init__(self, *args):  # either (unit_formatter, parent) or (parent)
        if len(args) == 1:
            parent = args[0]
            unit_formatter = None
        elif len(args) == 2:
            unit_formatter, parent = args
        else:
            raise TypeError()

        super().__init__(parent)

        # set an initial unit formatter to ease the set_unit_formatter call
        self.unit_formatter = asphodel.nativelib.create_custom_unit_formatter(
            1.0, 0.0, 0.0, "", "", "")

        self.validator = QtGui.QDoubleValidator(self)

        self.set_unit_formatter(unit_formatter)

    def set_unit_formatter(self, unit_formatter):
        value = self.value()
        minimum = self.minimum()
        maximum = self.maximum()

        scaled_value = (value * self.unit_formatter.conversion_scale +
                        self.unit_formatter.conversion_offset)

        if unit_formatter is None:
            unit_formatter = asphodel.nativelib.create_custom_unit_formatter(
                1.0, 0.0, 0.0, "", "", "")

        self.unit_formatter = unit_formatter
        if self.unit_formatter.unit_utf8:
            self.setSuffix(" " + self.unit_formatter.unit_utf8)
        else:
            self.setSuffix("")

        value = ((scaled_value - self.unit_formatter.conversion_offset) /
                 self.unit_formatter.conversion_scale)

        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)

    def setMinimum(self, value):
        scaled_value = (value * self.unit_formatter.conversion_scale +
                        self.unit_formatter.conversion_offset)
        self.validator.setBottom(scaled_value)
        return super().setMinimum(value)

    def setMaximum(self, value):
        scaled_value = (value * self.unit_formatter.conversion_scale +
                        self.unit_formatter.conversion_offset)
        self.validator.setTop(scaled_value)
        return super().setMaximum(value)

    def textFromValue(self, value):
        scaled_value = (value * self.unit_formatter.conversion_scale +
                        self.unit_formatter.conversion_offset)
        return self.unit_formatter.format_bare(scaled_value)

    def valueFromText(self, text):
        # remove the suffix, if any
        if self.suffix():
            s = text.rsplit(self.suffix(), 1)[0]
        else:
            s = text

        scaled_value = float(s)
        value = ((scaled_value - self.unit_formatter.conversion_offset) /
                 self.unit_formatter.conversion_scale)
        return round(value)

    def validate(self, input_text, pos):
        # remove the suffix, if any
        if self.suffix():
            remove_suffix = input_text.endswith(self.suffix())
            if remove_suffix:
                s = input_text.rsplit(self.suffix(), 1)[0]
            else:
                s = input_text
        else:
            remove_suffix = False
            s = input_text

        ret = self.validator.validate(s, pos)

        if remove_suffix:
            return (ret[0], ret[1] + self.suffix(), ret[2])
        else:
            return ret


class UnitFormatterDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, *args):  # either (unit_formatter, parent) or (parent)
        if len(args) == 1:
            parent = args[0]
            unit_formatter = None
        elif len(args) == 2:
            unit_formatter, parent = args
        else:
            raise TypeError()

        super().__init__(parent)

        # set an initial unit formatter to ease the set_unit_formatter call
        self.unit_formatter = asphodel.nativelib.create_custom_unit_formatter(
            1.0, 0.0, 0.0, "", "", "")

        self.validator = QtGui.QDoubleValidator(self)
        self.setDecimals(1000)

        self.set_unit_formatter(unit_formatter)

    def set_unit_formatter(self, unit_formatter):
        value = self.value()
        minimum = self.minimum()
        maximum = self.maximum()

        scaled_value = (value * self.unit_formatter.conversion_scale +
                        self.unit_formatter.conversion_offset)

        if unit_formatter is None:
            unit_formatter = asphodel.nativelib.create_custom_unit_formatter(
                1.0, 0.0, 0.0, "", "", "")

        self.unit_formatter = unit_formatter
        if self.unit_formatter.unit_utf8:
            self.setSuffix(" " + self.unit_formatter.unit_utf8)
        else:
            self.setSuffix("")

        value = ((scaled_value - self.unit_formatter.conversion_offset) /
                 self.unit_formatter.conversion_scale)

        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(value)

    def setMinimum(self, value):
        scaled_value = (value * self.unit_formatter.conversion_scale +
                        self.unit_formatter.conversion_offset)
        self.validator.setBottom(scaled_value)
        return super().setMinimum(value)

    def setMaximum(self, value):
        scaled_value = (value * self.unit_formatter.conversion_scale +
                        self.unit_formatter.conversion_offset)
        self.validator.setTop(scaled_value)
        return super().setMaximum(value)

    def textFromValue(self, value):
        if self.unit_formatter:
            scaled_value = (value * self.unit_formatter.conversion_scale +
                            self.unit_formatter.conversion_offset)
            return self.unit_formatter.format_bare(scaled_value)
        else:
            return str(value)

    def valueFromText(self, text):
        # remove the suffix, if any
        if self.suffix():
            s = text.rsplit(self.suffix(), 1)[0]
        else:
            s = text

        scaled_value = float(s)
        value = ((scaled_value - self.unit_formatter.conversion_offset) /
                 self.unit_formatter.conversion_scale)
        return value

    def validate(self, input_text, pos):
        # remove the suffix, if any
        if self.suffix():
            remove_suffix = input_text.endswith(self.suffix())
            if remove_suffix:
                s = input_text.rsplit(self.suffix(), 1)[0]
            else:
                s = input_text
        else:
            remove_suffix = False
            s = input_text

        # extra checks to allow for inf and -inf
        if math.isinf(self.validator.bottom()):
            if s == "-inf":
                # acceptable
                return (QtGui.QValidator.State.Acceptable, input_text, pos)
            elif "-inf".startswith(s):
                return (QtGui.QValidator.State.Intermediate, input_text, pos)
        if math.isinf(self.validator.top()):
            if s == "inf":
                # acceptable
                return (QtGui.QValidator.State.Acceptable, input_text, pos)
            elif "inf".startswith(s):
                return (QtGui.QValidator.State.Intermediate, input_text, pos)

        ret = self.validator.validate(s, pos)

        if remove_suffix:
            return (ret[0], ret[1] + self.suffix(), ret[2])
        else:
            return ret
