from PySide2 import QtCore, QtWidgets

import asphodel

from .preferences import read_bool_setting, write_bool_setting

from .ui_unit_preferences_widget import Ui_UnitPreferencesWidget

# NOTE: code can only display one alternate unit per unit type in the dialog
alternate_units = [
    {"unit_type": asphodel.UNIT_TYPE_WATT,
     "setting_name": "UseHorsepower",
     "scale": 1 / 746.0,
     "offset": 0.0,
     "unit_strings": ("HP", "HP", "HP")},
    {"unit_type": asphodel.UNIT_TYPE_M_PER_S2,
     "setting_name": "UseGForce",
     "scale": 1 / 9.80665,
     "offset": 0.0,
     "unit_strings": ("g", "g", "<b>g</b>")},
    {"unit_type": asphodel.UNIT_TYPE_HZ,
     "setting_name": "UseCPM",
     "scale": 60.0,
     "offset": 0.0,
     "unit_strings": ("CPM", "CPM", "CPM")},
    {"unit_type": asphodel.UNIT_TYPE_METER,
     "setting_name": "UseInch",
     "scale": 39.3700787401575,
     "offset": 0.0,
     "unit_strings": ("in", "in", "in")},
    {"unit_type": asphodel.UNIT_TYPE_GRAM,
     "setting_name": "UseOunce",
     "scale": 0.035273961949580414,
     "offset": 0.0,
     "unit_strings": ("oz", "oz", "oz")},
    {"unit_type": asphodel.UNIT_TYPE_M3_PER_S,
     "setting_name": "UseGPM",
     "scale": 15850.323141489,
     "offset": 0.0,
     "unit_strings": ("gal/min", "gal/min", "gal/min")},
    {"unit_type": asphodel.UNIT_TYPE_NEWTON_METER,
     "setting_name": "UseLbfIn",
     "scale": 8.850745780434613,
     "offset": 0.0,
     "unit_strings": ("lbf*in", b"lbf\xe2\x8b\x85in".decode("utf-8"),
                      "lbf&#8901;in")},
]


def create_unit_formatter(settings, unit_type, minimum, maximum, resolution):
    use_mixed = read_bool_setting(settings, "UseMixed", False)
    use_metric = read_bool_setting(settings, "UseMetric", True)

    if use_mixed:
        for alternate_unit in alternate_units:
            if unit_type == alternate_unit['unit_type']:
                use_alternate = read_bool_setting(
                    settings, alternate_unit['setting_name'], False)
                if use_alternate:
                    return asphodel.nativelib.create_custom_unit_formatter(
                        alternate_unit["scale"], alternate_unit["offset"],
                        resolution, *alternate_unit["unit_strings"])

        setting_name = "UseMetricType{}".format(unit_type)
        type_metric = read_bool_setting(settings, setting_name,
                                        use_metric)
        return asphodel.nativelib.create_unit_formatter(
            unit_type, minimum, maximum, resolution, use_metric=type_metric)

    return asphodel.nativelib.create_unit_formatter(
        unit_type, minimum, maximum, resolution, use_metric=use_metric)


class UnitPreferencesWidget(QtWidgets.QWidget, Ui_UnitPreferencesWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.settings = QtCore.QSettings()

        # key: unit type, value: {"group": Q button group,
        #                         "metric": button,
        #                         "us": button,
        #                         "alt": button or None,
        #                         "alt_setting": setting string or None}
        self.unit_buttons = {}

        self.setupUi(self)

        self.create_unit_buttons()

        self.metricUnits.toggled.connect(self.toggled_metric)
        self.usUnits.toggled.connect(self.toggled_us)
        self.mixedUnits.toggled.connect(self.toggled_mixed)

        self.unitGridLayout.setColumnStretch(0, 1)
        self.unitGridLayout.setColumnStretch(1, 1)
        self.unitGridLayout.setColumnStretch(2, 1)

        self.read_settings()

    def create_unit_buttons(self):
        for unit_type_name in asphodel.unit_type_names:
            unit_type = getattr(asphodel, unit_type_name)

            metric_formatter = asphodel.nativelib.create_unit_formatter(
                unit_type, 0.0, 0.0, 0.0, use_metric=True)
            us_formatter = asphodel.nativelib.create_unit_formatter(
                unit_type, 0.0, 0.0, 0.0, use_metric=False)

            # see if there's an alternate type for this button
            alt_button = None
            alt_setting = None
            for alternate_unit in alternate_units:
                if unit_type == alternate_unit['unit_type']:
                    alt_setting = alternate_unit['setting_name']
                    alt_button = QtWidgets.QRadioButton(self)
                    alt_name = alternate_unit['unit_strings'][1]  # UTF-8
                    metric_relation = metric_formatter.format_utf8(
                        1 / alternate_unit['scale'])
                    alt_text = "{} ({})".format(alt_name, metric_relation)
                    alt_button.setText(alt_text)
                    break

            if metric_formatter != us_formatter:
                # need two buttons
                row_count = self.unitGridLayout.rowCount()
                button_group = QtWidgets.QButtonGroup(self)

                metric_button = QtWidgets.QRadioButton(self)
                button_group.addButton(metric_button)
                metric_button.setText(metric_formatter.unit_utf8)
                self.unitGridLayout.addWidget(metric_button, row_count, 0)

                us_button = QtWidgets.QRadioButton(self)
                button_group.addButton(us_button)
                us_button.setText(us_formatter.unit_utf8)
                self.unitGridLayout.addWidget(us_button, row_count, 1)

                if alt_button:
                    button_group.addButton(alt_button)
                    self.unitGridLayout.addWidget(alt_button, row_count, 2)

                button_dict = {"group": button_group,
                               "metric": metric_button,
                               "us": us_button,
                               "alt": alt_button,
                               "alt_setting": alt_setting}
                self.unit_buttons[unit_type] = button_dict
            elif alt_button is not None:
                # need a combined metric/us button
                row_count = self.unitGridLayout.rowCount()
                button_group = QtWidgets.QButtonGroup(self)

                metric_us_button = QtWidgets.QRadioButton(self)
                button_group.addButton(metric_us_button)
                metric_us_button.setText(metric_formatter.unit_utf8)
                self.unitGridLayout.addWidget(metric_us_button, row_count, 0,
                                              1, 2)

                if alt_button:
                    button_group.addButton(alt_button)
                    self.unitGridLayout.addWidget(alt_button, row_count, 2)

                button_dict = {"group": button_group,
                               "metric": metric_us_button,
                               "us": metric_us_button,
                               "alt": alt_button,
                               "alt_setting": alt_setting}
                self.unit_buttons[unit_type] = button_dict

    def read_settings(self):
        use_mixed = read_bool_setting(self.settings, "UseMixed", False)
        use_metric = read_bool_setting(self.settings, "UseMetric", True)

        if use_mixed:
            self.mixedUnits.setChecked(True)

            # load unit settings
            for unit_type, button_dict in self.unit_buttons.items():
                if button_dict["alt"] is not None:
                    use_alt = read_bool_setting(
                        self.settings, button_dict["alt_setting"], False)
                    if use_alt:
                        button_dict["alt"].setChecked(True)
                else:
                    use_alt = False

                if not use_alt:
                    setting_name = "UseMetricType{}".format(unit_type)
                    type_metric = read_bool_setting(
                        self.settings, setting_name, use_metric)
                    if type_metric:
                        button_dict["metric"].setChecked(True)
                    else:
                        button_dict["us"].setChecked(True)
        else:
            if use_metric:
                self.metricUnits.setChecked(True)
            else:
                self.usUnits.setChecked(True)

    def write_settings(self):
        use_mixed = self.mixedUnits.isChecked()
        write_bool_setting(self.settings, "UseMixed", use_mixed)

        if use_mixed:
            for unit_type, button_dict in self.unit_buttons.items():
                if button_dict["alt"] is not None:
                    use_alt = button_dict["alt"].isChecked()
                    write_bool_setting(self.settings,
                                       button_dict["alt_setting"], use_alt)
                else:
                    use_alt = False

                if not use_alt:
                    if button_dict["metric"] is not button_dict["us"]:
                        setting_name = "UseMetricType{}".format(unit_type)
                        type_metric = button_dict["metric"].isChecked()
                        write_bool_setting(self.settings, setting_name,
                                           type_metric)
        else:
            use_metric = self.metricUnits.isChecked()
            write_bool_setting(self.settings, "UseMetric", use_metric)

    def toggled_metric(self, _junk=None):
        if self.metricUnits.isChecked():
            for button_dict in self.unit_buttons.values():
                button_dict['metric'].setChecked(True)

                button_dict['metric'].setEnabled(False)
                button_dict['us'].setEnabled(False)
                if button_dict['alt'] is not None:
                    button_dict['alt'].setEnabled(False)

    def toggled_us(self, _junk=None):
        if self.usUnits.isChecked():
            for button_dict in self.unit_buttons.values():
                button_dict['us'].setChecked(True)

                button_dict['metric'].setEnabled(False)
                button_dict['us'].setEnabled(False)
                if button_dict['alt'] is not None:
                    button_dict['alt'].setEnabled(False)

    def toggled_mixed(self, _junk=None):
        if self.mixedUnits.isChecked():
            for button_dict in self.unit_buttons.values():
                button_dict['metric'].setEnabled(True)
                button_dict['us'].setEnabled(True)
                if button_dict['alt'] is not None:
                    button_dict['alt'].setEnabled(True)
