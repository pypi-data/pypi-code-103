from typing import Optional
import os
import logging

from PySide2 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

from hyo2.abc.app.widgets.browser.download_widget import DownloadWidget
from hyo2.abc.lib.lib_info import LibInfo
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


class WebEnginePage(QtWebEngineWidgets.QWebEnginePage):

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if ("slideshare" not in sourceID) and ("hydroffice.org" not in sourceID):
            logger.debug("QWebEngine: %s[#%d] -> %s" % (sourceID, lineNumber, message))


class Browser(QtWidgets.QMainWindow):

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, url: str = "https://www.hydroffice.org") -> None:
        super().__init__(parent)

        self.setWindowTitle('Browser')

        self._actions = {}
        self._create_menu()

        self._tool_bar = QtWidgets.QToolBar()
        self._tool_bar.setIconSize(QtCore.QSize(16, 16))
        self.addToolBar(self._tool_bar)
        for action in self._actions.values():
            if not action.icon().isNull():
                self._tool_bar.addAction(action)

        self.address_line_edit = QtWidgets.QLineEdit()
        self.address_line_edit.setClearButtonEnabled(True)
        # noinspection PyUnresolvedReferences
        self.address_line_edit.returnPressed.connect(self._load)
        self._tool_bar.addWidget(self.address_line_edit)

        self.view = QtWebEngineWidgets.QWebEngineView()
        # self.view.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled, True)
        # self.view.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.FullScreenSupportEnabled, True)
        # self.view.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.AllowRunningInsecureContent, True)
        # self.view.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.SpatialNavigationEnabled, True)
        self.view.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.JavascriptEnabled, True)
        self.view.settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.JavascriptCanOpenWindows, True)
        self.view.settings().setAttribute(
            QtWebEngineWidgets.QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.view.settings().setAttribute(
            QtWebEngineWidgets.QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        # self.interceptor = RequestInterceptor()
        self.profile = QtWebEngineWidgets.QWebEngineProfile()
        # self.profile.setRequestInterceptor(self.interceptor)
        # noinspection PyUnresolvedReferences
        self.profile.downloadRequested.connect(self._download_requested)
        self.profile.setPersistentCookiesPolicy(QtWebEngineWidgets.QWebEngineProfile.NoPersistentCookies)
        self.profile.setHttpCacheType(QtWebEngineWidgets.QWebEngineProfile.NoCache)
        self.profile.setPersistentStoragePath(self._web_engine_folder())
        self.page = WebEnginePage(self.profile, self.view)
        self.view.setPage(self.page)

        # noinspection PyUnresolvedReferences
        self.view.page().titleChanged.connect(self.setWindowTitle)
        # noinspection PyUnresolvedReferences
        self.view.page().urlChanged.connect(self._url_changed)
        self.setCentralWidget(self.view)

        self.change_url(url=url)

    @classmethod
    def _web_engine_folder(cls) -> str:
        dir_path = os.path.abspath(os.path.join(Helper(lib_info=LibInfo()).hydroffice_folder(), "WebEngine"))
        if not os.path.exists(dir_path):  # create it if it does not exist
            os.makedirs(dir_path)
        return dir_path

    def _create_menu(self) -> None:
        style_icons = ':/qt-project.org/styles/commonstyle/images/'

        # noinspection PyCallByClass,PyTypeChecker
        back_action = QtWidgets.QAction(QtGui.QIcon.fromTheme("go-previous", QtGui.QIcon(style_icons + 'left-32.png')),
                                        "Back", self, shortcut=QtGui.QKeySequence(QtGui.QKeySequence.Back),
                                        triggered=self.back)

        self._actions[QtWebEngineWidgets.QWebEnginePage.Back] = back_action

        # noinspection PyCallByClass,PyTypeChecker
        forward_action = QtWidgets.QAction(QtGui.QIcon.fromTheme("go-next", QtGui.QIcon(style_icons + 'right-32.png')),
                                           "Forward", self, shortcut=QtGui.QKeySequence(QtGui.QKeySequence.Forward),
                                           triggered=self.forward)
        self._actions[QtWebEngineWidgets.QWebEnginePage.Forward] = forward_action

        reload_action = QtWidgets.QAction(QtGui.QIcon(style_icons + 'refresh-32.png'), "Reload", self,
                                          shortcut=QtGui.QKeySequence(QtGui.QKeySequence.Refresh),
                                          triggered=self.reload)
        self._actions[QtWebEngineWidgets.QWebEnginePage.Reload] = reload_action

    def change_url(self, url: str) -> None:
        self.address_line_edit.setText(url)
        self._load()

    def url(self) -> str:
        return self.address_line_edit.text()

    def _load(self) -> None:
        url = QtCore.QUrl.fromUserInput(self.address_line_edit.text().strip())
        if url.isValid():
            self.view.load(url)

    def back(self) -> None:
        self.view.page().triggerAction(QtWebEngineWidgets.QWebEnginePage.Back)

    def forward(self) -> None:
        self.view.page().triggerAction(QtWebEngineWidgets.QWebEnginePage.Forward)

    def reload(self) -> None:
        self.view.page().triggerAction(QtWebEngineWidgets.QWebEnginePage.Reload)

    def _url_changed(self, url: QtCore.QUrl) -> None:
        self.address_line_edit.setText(url.toString())

    def _download_requested(self, item: QtWebEngineWidgets.QWebEngineDownloadItem) -> None:

        # Remove old downloads before opening a new one
        for old_download in self.statusBar().children():
            if type(old_download).__name__ == 'download_widget' and \
                    old_download.state() != QtWebEngineWidgets.QWebEngineDownloadItem.DownloadInProgress:
                self.statusBar().removeWidget(old_download)
                del old_download

        item.accept()
        download_widget = DownloadWidget(item)
        download_widget.remove_requested.connect(self._remove_download_requested,
                                                 QtCore.Qt.QueuedConnection)

        self.statusBar().addWidget(download_widget)

    def _remove_download_requested(self):
        download_widget = self.sender()
        self.statusBar().removeWidget(download_widget)
        del download_widget
