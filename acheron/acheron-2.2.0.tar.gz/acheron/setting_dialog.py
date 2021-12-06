import logging

from PySide2 import QtWidgets

from hyperborea.setting_widget import SettingWidget

from .ui_setting_dialog import Ui_SettingDialog

logger = logging.getLogger(__name__)


class SettingDialog(QtWidgets.QDialog, Ui_SettingDialog):
    def __init__(self, settings, nvm_bytes, custom_enums,
                 setting_categories, parent=None):
        super().__init__(parent)

        self.device_tab = parent
        self.settings = settings
        self.nvm_bytes = nvm_bytes
        self.custom_enums = custom_enums
        self.setting_categories = setting_categories

        self.setting_widgets = []

        self.setupUi(self)

        self.add_setting_widgets()

        b = self.buttonBox.button(QtWidgets.QDialogButtonBox.RestoreDefaults)
        b.clicked.connect(self.restore_defaults)

    def add_setting_widgets(self):
        remaining_settings = set(range(len(self.settings)))

        setting_tabs = []

        for name, category_settings in self.setting_categories:
            widgets = []
            for setting_index in category_settings:
                if setting_index in remaining_settings:
                    remaining_settings.remove(setting_index)

                    setting = self.settings[setting_index]
                    widget = SettingWidget(setting, self.nvm_bytes,
                                           self.custom_enums)
                    self.setting_widgets.append(widget)
                    widgets.append(widget.widgets)
            setting_tabs.append((name, widgets))

        if remaining_settings:
            remaining_widgets = []
            for setting_index in sorted(remaining_settings):
                setting = self.settings[setting_index]
                widget = SettingWidget(setting, self.nvm_bytes,
                                       self.custom_enums)
                self.setting_widgets.append(widget)
                remaining_widgets.append(widget.widgets)
            # add the default tab at the beginning
            setting_tabs.insert(0, ("Device Settings", remaining_widgets))

        for tab_name, widgets in setting_tabs:
            tab_widget = QtWidgets.QWidget()
            form_layout = QtWidgets.QFormLayout(tab_widget)

            for row_widgets in widgets:
                form_layout.addRow(*row_widgets)

            self.tabWidget.addTab(tab_widget, tab_name)

    def update_nvm(self, nvm_bytes):
        for widget in self.setting_widgets:
            widget.update_nvm(nvm_bytes)

    def restore_defaults(self):
        for widget in self.setting_widgets:
            widget.restore_defaults()
