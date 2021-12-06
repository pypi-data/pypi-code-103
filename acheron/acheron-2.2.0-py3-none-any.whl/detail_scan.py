import collections
import datetime
import logging

from PySide2 import QtCore, QtGui, QtWidgets

from . import radio_panel
from .ui_detail_scan_dialog import Ui_DetailScanDialog

logger = logging.getLogger(__name__)


class SortableTableWidgetItem(QtWidgets.QTableWidgetItem):
    def __init__(self):
        super().__init__()
        self.sort_value = None

    def __lt__(self, other):
        try:
            other_sort_value = other.sort_value
            if other_sort_value is not None and self.sort_value is not None:
                return self.sort_value < other_sort_value
        except AttributeError:
            pass
        # fall back
        return self.text() < other.text()


TableItems = collections.namedtuple(
    "TableItems", ["serial_number", "scan_strength", "tag1", "tag2",
                   "board_info", "build_info", "build_date", "bootloader",
                   "device_mode", "last_seen"])


class RowInformation:
    def __init__(self, table_items, scan, last_seen):
        self.table_items = table_items
        self.scan = scan
        self.last_seen = last_seen
        self.last_seen_seconds = None
        self.connected_radio = ""


class DetailScanDialog(QtWidgets.QDialog, Ui_DetailScanDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.row_info = {}  # key: serial_number, value RowInformation
        self.scans_to_process = collections.deque()

        self.setupUi(self)
        self.extra_ui_setup()

        self.selection_changed()

    def extra_ui_setup(self):
        self.bootloader_fg_brush = QtGui.QBrush(QtGui.QColor(QtCore.Qt.black))
        self.bootloader_bg_brush = QtGui.QBrush(QtGui.QColor(QtCore.Qt.yellow))
        self.stale_fg_brush = QtGui.QBrush(QtGui.QColor(QtCore.Qt.black))
        self.stale_bg_brush = QtGui.QBrush(QtGui.QColor(QtCore.Qt.yellow))
        self.old_fg_brush = QtGui.QBrush(QtGui.QColor(QtCore.Qt.black))
        self.old_bg_brush = QtGui.QBrush(QtGui.QColor(QtCore.Qt.red))

        self.default_font = QtGui.QFont()
        self.bootloader_font = QtGui.QFont()
        self.bootloader_font.setBold(True)

        header = self.tableWidget.horizontalHeader()
        header.setResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.clearButton = self.buttonBox.button(
            QtWidgets.QDialogButtonBox.Reset)
        self.clearButton.setText(self.tr("Clear"))
        self.clearButton.clicked.connect(self.clear_button_cb)

        radio_panel.active_scan_database.clear.connect(self.clear)
        radio_panel.active_scan_database.scan_result_ready.connect(
            self.active_scan_ready_cb)
        radio_panel.active_scan_database.update_connected_radio.connect(
            self.update_connected_radio)

        selection_model = self.tableWidget.selectionModel()
        selection_model.selectionChanged.connect(self.selection_changed)
        self.tableWidget.doubleClicked.connect(self.double_click_cb)

        self.tableWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.tableWidget.setSortingEnabled(True)

        self.update_timer = QtCore.QTimer(self)
        self.update_timer.timeout.connect(self.update_rows)
        self.update_timer.start(500)

        self.update_scan_count()

    def double_click_cb(self, index=None):
        self.accept()

    def get_selected_scan(self):
        rows = self.tableWidget.selectionModel().selectedRows()
        if rows:
            row = rows[0].row()
            item = self.tableWidget.item(row, 0)
            serial_number = item.sort_value
            return self.row_info[serial_number].scan
        else:
            return None

    def selection_changed(self, _selected=None, _deselected=None):
        ok_button = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        if self.tableWidget.selectionModel().hasSelection():
            ok_button.setEnabled(True)
        else:
            ok_button.setEnabled(False)

    def clear(self):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.row_info.clear()
        self.scans_to_process.clear()
        self.update_scan_count()

    def clear_button_cb(self):
        radio_panel.active_scan_database.clear_database()

    def handle_scan(self, scan, last_seen):
        row_info = self.row_info.get(scan.serial_number)
        if not row_info:
            table_items = self.add_row(scan.serial_number)
            row_info = RowInformation(table_items, None, last_seen)
            row_info.last_seen = last_seen
            self.row_info[scan.serial_number] = row_info
            self.update_scan_count()

            self.update_row_with_scan(row_info, scan)

            radio_sn = radio_panel.active_scan_database.get_connected_radio(
                scan.serial_number)
            if radio_sn:
                self.update_connected_radio(scan.serial_number, radio_sn)

            device_info = radio_panel.active_scan_database.get_scan_info(
                scan.serial_number)
            if device_info:
                self.active_scan_ready_cb(scan.serial_number, device_info)

            self.update_last_seen(row_info)
        else:
            row_info.last_seen = last_seen
            self.scans_to_process.append(scan)

    def update_row_with_scan(self, row_info, scan):
        old_scan = row_info.scan

        if old_scan is None or old_scan.scan_strength != scan.scan_strength:
            if scan.scan_strength is not None:
                # update scan strength
                item = row_info.table_items.scan_strength
                item.sort_value = scan.scan_strength
                item.setText("{} dBm".format(scan.scan_strength))

        if old_scan is None or old_scan.device_mode != scan.device_mode:
            # update device mode
            item = row_info.table_items.device_mode
            item.setData(QtCore.Qt.DisplayRole, scan.device_mode)

        if old_scan is None or old_scan.is_bootloader != scan.is_bootloader:
            item = row_info.table_items.bootloader
            if scan.is_bootloader:
                item.setData(QtCore.Qt.DisplayRole, "Running")
                item.setFont(self.bootloader_font)

                for item in row_info.table_items:
                    item.setForeground(self.bootloader_fg_brush)
                    item.setBackground(self.bootloader_bg_brush)
            else:
                item.setData(QtCore.Qt.DisplayRole, "")
                item.setFont(self.default_font)

                for item in row_info.table_items:
                    item.setData(QtCore.Qt.ForegroundRole, None)
                    item.setData(QtCore.Qt.BackgroundRole, None)

        row_info.scan = scan

    def add_row(self, serial_number):
        start_index = self.tableWidget.rowCount()
        self.tableWidget.insertRow(start_index)

        serial_number_item = SortableTableWidgetItem()
        serial_number_item.sort_value = serial_number
        serial_number_item.setData(QtCore.Qt.DisplayRole, serial_number)
        self.tableWidget.setItem(start_index, 0, serial_number_item)

        table_items = [serial_number_item]

        for i in range(1, self.tableWidget.columnCount()):
            if i in (1, 9):
                new_item = SortableTableWidgetItem()
            else:
                new_item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setItem(serial_number_item.row(), i, new_item)
            table_items.append(new_item)

        return TableItems(*table_items)

    def update_last_seen(self, row_info, now=None):
        if now is None:
            now = datetime.datetime.now(datetime.timezone.utc)

        delta = now - row_info.last_seen
        item = row_info.table_items.last_seen
        item.sort_value = delta

        seconds = int(delta.total_seconds())

        if seconds != row_info.last_seen_seconds:
            row_info.last_seen_seconds = seconds
            if seconds == 1:
                text = "1 second ago"
            else:
                text = "".join((str(seconds), " seconds ago"))
            item.setText(text)

            if seconds < 10:
                # normal
                if row_info.scan.is_bootloader:
                    item.setForeground(self.bootloader_fg_brush)
                    item.setBackground(self.bootloader_bg_brush)
                else:
                    # go back to default
                    item.setData(QtCore.Qt.ForegroundRole, None)
                    item.setData(QtCore.Qt.BackgroundRole, None)
            elif seconds < 30:
                item.setForeground(self.stale_fg_brush)
                item.setBackground(self.stale_bg_brush)
            else:
                item.setForeground(self.old_fg_brush)
                item.setBackground(self.old_bg_brush)

    def update_rows(self):
        self.tableWidget.setUpdatesEnabled(False)
        header = self.tableWidget.horizontalHeader()
        header.setResizeMode(QtWidgets.QHeaderView.Fixed)

        try:
            while True:
                scan = self.scans_to_process.popleft()
                row_info = self.row_info.get(scan.serial_number)
                if row_info:
                    self.update_row_with_scan(row_info, scan)
        except IndexError:
            pass

        now = datetime.datetime.now(datetime.timezone.utc)
        for row_info in self.row_info.values():
            if row_info.connected_radio:
                # skip connected ones
                continue

            self.update_last_seen(row_info, now)

        header.setResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget.setUpdatesEnabled(True)

    def active_scan_ready_cb(self, serial_number, device_info):
        row_info = self.row_info.get(serial_number)
        if row_info is None:
            return

        if device_info:
            # add active scan information
            user_tag_1 = device_info['user_tag_1']
            if user_tag_1 is None:
                user_tag_1 = ""
            row_info.table_items.tag1.setText(user_tag_1)
            user_tag_2 = device_info['user_tag_2']
            if user_tag_2 is None:
                user_tag_2 = ""
            row_info.table_items.tag2.setText(user_tag_2)
            board_info_str = "{} rev {}".format(*device_info['board_info'])
            row_info.table_items.board_info.setText(board_info_str)
            row_info.table_items.build_info.setText(device_info['build_info'])
            row_info.table_items.build_date.setText(device_info['build_date'])
        else:
            # remove active scan information
            row_info.table_items.tag1.setText("")
            row_info.table_items.tag2.setText("")
            row_info.table_items.board_info.setText("")
            row_info.table_items.build_info.setText("")
            row_info.table_items.build_date.setText("")

    def update_connected_radio(self, serial_number, connected_radio):
        row_info = self.row_info.get(serial_number)
        if row_info is None or row_info.connected_radio == connected_radio:
            return

        row_info.connected_radio = connected_radio

        if connected_radio:
            item = row_info.table_items.last_seen
            item.setText("Connected to {}".format(connected_radio))

            if row_info.scan.is_bootloader:
                item.setForeground(self.bootloader_fg_brush)
                item.setBackground(self.bootloader_bg_brush)
            else:
                # go back to default
                item.setData(QtCore.Qt.ForegroundRole, None)
                item.setData(QtCore.Qt.BackgroundRole, None)
        else:
            self.update_last_seen(row_info)

    def update_scan_count(self):
        self.clearButton.setText("Clear ({})".format(len(self.row_info)))
