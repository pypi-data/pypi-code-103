import logging
from osgeo import gdal
from PySide2 import QtCore, QtWidgets

logger = logging.getLogger(__name__)


class GdalInfoTab(QtWidgets.QWidget):

    def __init__(self, parent: QtWidgets.QWidget=None):
        super().__init__(parent)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # Top

        self.top_layout = QtWidgets.QHBoxLayout()

        self.layout.addLayout(self.top_layout)
        self.version_groupbox = QtWidgets.QGroupBox(self)
        self.version_groupbox.setTitle("Version")
        self.top_layout.addWidget(self.version_groupbox)
        self.version_layout = QtWidgets.QVBoxLayout()
        self.version_groupbox.setLayout(self.version_layout)
        self.version_release = QtWidgets.QLabel("Release: %s" % gdal.VersionInfo('RELEASE_NAME'))
        self.version_layout.addWidget(self.version_release)
        self.version_date = QtWidgets.QLabel("Date: %s" % gdal.VersionInfo('RELEASE_DATE'))
        self.version_layout.addWidget(self.version_date)

        self.cache_groupbox = QtWidgets.QGroupBox(self)
        self.cache_groupbox.setTitle("Cache")
        self.top_layout.addWidget(self.cache_groupbox)
        self.cache_layout = QtWidgets.QVBoxLayout()
        self.cache_groupbox.setLayout(self.cache_layout)
        self.cache_max = QtWidgets.QLabel("Max: %.1f MB" % (gdal.GetCacheMax() / (1024 * 1024),))
        self.cache_layout.addWidget(self.cache_max)
        self.cache_used = QtWidgets.QLabel("Used: %.1f MB" % (gdal.GetCacheUsed() / (1024 * 1024),))
        self.cache_layout.addWidget(self.cache_used)

        # Bottom

        self.bottom_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.bottom_layout)

        self.drivers_groupbox = QtWidgets.QGroupBox(self)
        self.drivers_groupbox.setTitle("Drivers")
        self.bottom_layout.addWidget(self.drivers_groupbox)
        self.drivers_layout = QtWidgets.QVBoxLayout()
        self.drivers_groupbox.setLayout(self.drivers_layout)
        self.drivers_count = QtWidgets.QLabel("Number of drivers: %d" % (gdal.GetDriverCount(),))
        self.drivers_layout.addWidget(self.drivers_count)

        self.table = QtWidgets.QTableWidget(self)
        self.table.setObjectName("GdalDriversTable")
        self.table.setColumnCount(8)
        self.table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Short Name")
        self.table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Long Name")
        self.table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Help Page")
        self.table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Mime Type")
        self.table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Extensions")
        self.table.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Data Types")
        self.table.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Creation Options")
        self.table.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Metadata")
        self.table.setHorizontalHeaderItem(7, item)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setVisible(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setRowCount(gdal.GetDriverCount())
        for row in range(gdal.GetDriverCount()):
            driver = gdal.GetDriver(row)
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(driver.ShortName))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(driver.LongName))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(driver.HelpTopic))

            metadata = driver.GetMetadata()
            if metadata:
                self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(metadata.pop(gdal.DMD_MIMETYPE, ''))))
                self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(metadata.pop(gdal.DMD_EXTENSION, ''))))
                self.table.setItem(row, 5,
                                   QtWidgets.QTableWidgetItem(str(metadata.pop(gdal.DMD_CREATIONDATATYPES, ''))))

                full_data = metadata.pop(gdal.DMD_CREATIONOPTIONLIST, '')
                if full_data:
                    data = full_data[:10] + "[..]"
                else:
                    data = full_data
                table_item = QtWidgets.QTableWidgetItem(data)
                table_item.setToolTip(full_data)
                self.table.setItem(row, 6, table_item)

                metadata_list = ['%s=%s' % (k, v) for k, v in metadata.items()]
                metadata = ", ".join(metadata_list)[:10] + "[..]"
                table_item = QtWidgets.QTableWidgetItem(metadata)
                table_item.setToolTip('\n'.join(metadata_list))
                self.table.setItem(row, 7, table_item)

        self.table.horizontalHeader().resizeSections(QtWidgets.QHeaderView.ResizeToContents)
        self.table.setSortingEnabled(True)
        self.table.sortItems(0, QtCore.Qt.AscendingOrder)
        self.drivers_layout.addWidget(self.table)
