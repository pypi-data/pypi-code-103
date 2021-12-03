from AnyQt.QtWidgets import QFrame

from Orange.data import Table
from Orange.preprocess.remove import Remove
from Orange.widgets import gui, widget
from Orange.widgets.settings import Setting
from Orange.widgets.utils.sql import check_sql_input
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets.widget import Input, Output
from Orange.i18n_config import *


def __(key):
    return i18n.t("widget.data.data.owpurgedomain." + key)

class OWPurgeDomain(widget.OWWidget):
    name = __("name")
    description = __("desc")
    icon = "icons/PurgeDomain.svg"
    category = "Data"
    keywords = ["remove", "delete", "unused"]

    class Inputs:
        data = Input("Data", Table, label=i18n.t("widget.data.data.common.data"))

    class Outputs:
        data = Output("Data", Table, label=i18n.t("widget.data.data.common.data"))

    removeValues = Setting(1)
    removeAttributes = Setting(1)
    removeClasses = Setting(1)
    removeClassAttribute = Setting(1)
    removeMetaAttributeValues = Setting(1)
    removeMetaAttributes = Setting(1)
    autoSend = Setting(True)
    sortValues = Setting(True)
    sortClasses = Setting(True)

    want_main_area = False
    resizing_enabled = False

    feature_options = (('sortValues', __('option.sort_categorical_feature')),
                       ('removeValues', __('option.remove_unused_feature')),
                       ('removeAttributes', __('option.remove_constant_feature')))

    class_options = (('sortClasses', __('option.sort_class_value')),
                     ('removeClasses', __('option.remove_unused_class')),
                     ('removeClassAttribute', __('option.remove_constant_var')))

    meta_options = (('removeMetaAttributeValues', __('option.reomve_unused_attr')),
                    ('removeMetaAttributes', __('option.remove_constant_attr')))

    stat_labels = ((__('label.sort_feature'), 'resortedAttrs'),
                   (__('label.reduce_feature'), 'reducedAttrs'),
                   (__('label.remove_feature'), 'removedAttrs'),
                   (__('label.sort_class'), 'resortedClasses'),
                   (__('label.reduce_class'), 'reducedClasses'),
                   (__('label.remove_class'), 'removedClasses'),
                   (__('label.reduce_meta'), 'reducedMetas'),
                   (__('label.remove_meta'), 'removedMetas'))

    def __init__(self):
        super().__init__()
        self.data = None

        self.removedAttrs = "-"
        self.reducedAttrs = "-"
        self.resortedAttrs = "-"
        self.removedClasses = "-"
        self.reducedClasses = "-"
        self.resortedClasses = "-"
        self.removedMetas = "-"
        self.reducedMetas = "-"

        def add_line(parent):
            frame = QFrame()
            frame.setFrameShape(QFrame.HLine)
            frame.setFrameShadow(QFrame.Sunken)
            parent.layout().addWidget(frame)

        boxAt = gui.vBox(self.controlArea, i18n.t("common.general.features"))
        for value, label in self.feature_options:
            gui.checkBox(boxAt, self, value, label,
                         callback=self.commit.deferred)
        add_line(boxAt)
        gui.label(boxAt, self, __('label.sort_reduce_remove'))

        boxAt = gui.vBox(self.controlArea, i18n.t("common.general.classes"))
        for value, label in self.class_options:
            gui.checkBox(boxAt, self, value, label,
                         callback=self.commit.deferred)
        add_line(boxAt)
        gui.label(boxAt, self, __('label.sort_reduce_remove'))

        boxAt = gui.vBox(self.controlArea, __("box.meta_attribute"))
        for value, label in self.meta_options:
            gui.checkBox(boxAt, self, value, label,
                         callback=self.commit.deferred)
        add_line(boxAt)
        gui.label(boxAt, self, __('label.reduce_remove'))

        gui.auto_send(self.buttonsArea, self, "autoSend")

    @Inputs.data
    @check_sql_input
    def setData(self, dataset):
        if dataset is not None:
            self.data = dataset
            self.commit.now()
        else:
            self.removedAttrs = "-"
            self.reducedAttrs = "-"
            self.resortedAttrs = "-"
            self.removedClasses = "-"
            self.reducedClasses = "-"
            self.resortedClasses = "-"
            self.removedMetas = "-"
            self.reducedMetas = "-"
            self.Outputs.data.send(None)
            self.data = None

    @gui.deferred
    def commit(self):
        if self.data is None:
            return

        attr_flags = sum([Remove.SortValues * self.sortValues,
                          Remove.RemoveConstant * self.removeAttributes,
                          Remove.RemoveUnusedValues * self.removeValues])
        class_flags = sum([Remove.SortValues * self.sortClasses,
                           Remove.RemoveConstant * self.removeClassAttribute,
                           Remove.RemoveUnusedValues * self.removeClasses])
        meta_flags = sum([Remove.RemoveConstant * self.removeMetaAttributes,
                          Remove.RemoveUnusedValues * self.removeMetaAttributeValues])
        remover = Remove(attr_flags, class_flags, meta_flags)
        cleaned = remover(self.data)
        attr_res, class_res, meta_res = \
            remover.attr_results, remover.class_results, remover.meta_results

        self.removedAttrs = attr_res['removed']
        self.reducedAttrs = attr_res['reduced']
        self.resortedAttrs = attr_res['sorted']

        self.removedClasses = class_res['removed']
        self.reducedClasses = class_res['reduced']
        self.resortedClasses = class_res['sorted']

        self.removedMetas = meta_res['removed']
        self.reducedMetas = meta_res['reduced']

        self.Outputs.data.send(cleaned)

    def send_report(self):
        def list_opts(opts):
            return "; ".join(label.lower()
                             for value, label in opts
                             if getattr(self, value)) or "no changes"

        self.report_items(i18n.t("common.software.setting"), (
            (i18n.t("common.general.features"), list_opts(self.feature_options)),
            (i18n.t("common.general.classes"), list_opts(self.class_options)),
            (__("report.meta"), list_opts(self.meta_options))))
        if self.data:
            self.report_items(i18n.t("common.general.statistics"), (
                (label, getattr(self, value))
                for label, value in self.stat_labels
            ))


if __name__ == "__main__":  # pragma: no cover
    data = Table.from_url("https://datasets.biolab.si/core/car.tab")
    subset = [inst for inst in data if inst["buying"] == "v-high"]
    subset = Table(data.domain, subset)
    # The "buying" should be removed and the class "y" reduced
    WidgetPreview(OWPurgeDomain).run(subset)
