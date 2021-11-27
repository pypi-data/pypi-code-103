import sys
from PySide2 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets


class DownloadWidget(QtWidgets.QProgressBar):
    finished = QtCore.Signal()
    remove_requested = QtCore.Signal()

    def __init__(self, download_item: QtWebEngineWidgets.QWebEngineDownloadItem) -> None:
        super(DownloadWidget, self).__init__()
        self._download_item = download_item
        # noinspection PyUnresolvedReferences
        download_item.finished.connect(self._finished)
        # noinspection PyUnresolvedReferences
        download_item.downloadProgress.connect(self._download_progress)
        # noinspection PyUnresolvedReferences
        download_item.stateChanged.connect(self._update_tool_tip())
        path = download_item.path()

        self.setMaximumWidth(300)
        # Shorten the file name
        description = QtCore.QFileInfo(path).fileName()
        description_length = len(description)
        if description_length > 30:
            description = '{}...{}'.format(description[0:10], description[description_length - 10:])

        self.setFormat('{} %p%'.format(description))
        self.setOrientation(QtCore.Qt.Horizontal)
        self.setMinimum(0)
        self.setValue(0)
        self.setMaximum(100)
        self._update_tool_tip()

        # Force progress bar text to be shown on macoS by using 'fusion' style
        if sys.platform == 'darwin':
            # noinspection PyCallByClass,PyTypeChecker
            self.setStyle(QtWidgets.QStyleFactory.create('fusion'))

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.customContextMenuRequested.connect(self.context_menu_event)

    @classmethod
    def open_file(cls, file: str) -> None:
        # noinspection PyTypeChecker,PyCallByClass
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(file))

    @classmethod
    def open_download_directory(cls) -> None:
        path = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DownloadLocation)
        cls.open_file(path)

    def _finished(self) -> None:
        self._update_tool_tip()
        # noinspection PyUnresolvedReferences
        self.finished.emit()

    def _download_progress(self, bytes_received: int, bytes_total: int) -> None:
        self.setValue(int(100 * bytes_received / bytes_total))

    def _update_tool_tip(self) -> None:
        path = self._download_item.path()
        tool_tip = "{}\n{}".format(self._download_item.url().toString(),
                                   QtCore.QDir.toNativeSeparators(path))
        total_bytes = self._download_item.totalBytes()
        if total_bytes > 0:
            tool_tip += "\n{}K".format(total_bytes / 1024)
        state = self._download_item.state()
        if state == QtWebEngineWidgets.QWebEngineDownloadItem.DownloadRequested:
            tool_tip += "\n(requested)"
        elif state == QtWebEngineWidgets.QWebEngineDownloadItem.DownloadInProgress:
            tool_tip += "\n(downloading)"
        elif state == QtWebEngineWidgets.QWebEngineDownloadItem.DownloadCompleted:
            tool_tip += "\n(completed)"
        elif state == QtWebEngineWidgets.QWebEngineDownloadItem.DownloadCancelled:
            tool_tip += "\n(cancelled)"
        else:
            tool_tip += "\n(interrupted)"

        self.setToolTip(tool_tip)

    def _launch(self) -> None:
        self.open_file(self._download_item.path())

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:

        if self._download_item.state() == QtWebEngineWidgets.QWebEngineDownloadItem.DownloadCompleted:
            self._launch()

        event.ignore()

    def context_menu_event(self, event: QtGui.QMouseEvent) -> None:
        state = self._download_item.state()
        context_menu = QtWidgets.QMenu()
        launch_action = context_menu.addAction("Launch")
        launch_action.setEnabled(state == QtWebEngineWidgets.QWebEngineDownloadItem.DownloadCompleted)
        show_in_folder_action = context_menu.addAction("Show in Folder")
        show_in_folder_action.setEnabled(state == QtWebEngineWidgets.QWebEngineDownloadItem.DownloadCompleted)
        cancel_action = context_menu.addAction("Cancel")
        cancel_action.setEnabled(state == QtWebEngineWidgets.QWebEngineDownloadItem.DownloadInProgress)
        remove_action = context_menu.addAction("Remove")
        remove_action.setEnabled(state != QtWebEngineWidgets.QWebEngineDownloadItem.DownloadInProgress)

        chosen_action = context_menu.exec_(self.mapToGlobal(event))
        if chosen_action == launch_action:
            self._launch()
        elif chosen_action == show_in_folder_action:
            self.open_file(QtCore.QFileInfo(self._download_item.path()).absolutePath())
        elif chosen_action == cancel_action:
            self._download_item.cancel()
        elif chosen_action == remove_action:
            # noinspection PyUnresolvedReferences
            self.remove_requested.emit()
