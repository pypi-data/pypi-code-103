import logging

from PySide2.QtCore import QEventLoop, QTimer, QUrl
from PySide2.QtWidgets import QApplication
from PySide2.QtWebEngineWidgets import QWebEnginePage, QWebEngineView, QWebEngineSettings

logger = logging.getLogger(__name__)


class WebEnginePage(QWebEnginePage):

    def javaScriptConsoleMessage(self, level, message, line_number, source_id):
        if ("slideshare" not in source_id) and ("hydroffice.org" not in source_id):
            logger.debug("QWebEngine: %s[#%d] -> %s" % (source_id, line_number, message))


class WebRenderer(QWebEngineView):

    def __init__(self, make_app: bool = False):
        if make_app:
            # os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-logging --log-level=3"
            self._app = QApplication([])
        QWebEngineView.__init__(self)

        self.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

        self.page = WebEnginePage(self)
        self.setPage(self.page)

    def open(self, url: str, timeout: int = 10):
        """Wait for download to complete and return result"""
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        # noinspection PyUnresolvedReferences
        timer.timeout.connect(loop.quit)
        # noinspection PyUnresolvedReferences
        self.loadFinished.connect(loop.quit)
        self.load(QUrl(url))
        # noinspection PyArgumentList
        timer.start(timeout * 1000)
        loop.exec_()  # delay here until download finished
        if timer.isActive():
            # downloaded successfully
            timer.stop()
        else:
            logger.info('Request timed out: %s' % url)
