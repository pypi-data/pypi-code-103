from datetime import datetime
import email
import os
import traceback
from types import TracebackType
from typing import Optional, Sequence, Union
from PySide2 import QtCore, QtGui, QtWidgets

import logging

from hyo2.abc.app.app_info import AppInfo
from hyo2.abc.lib.lib_info import LibInfo
from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


class ExceptionDialog(QtWidgets.QDialog):
    media = os.path.join(os.path.dirname(__file__), "media")

    def __init__(self, app_info: AppInfo, lib_info: LibInfo,
                 ex_type: Optional[type] = None, ex_value: Optional[BaseException] = None,
                 tb: Optional[TracebackType] = None, parent: Optional[QtCore.QObject] = None):
        super().__init__(parent)

        self._ai = app_info
        self._li = lib_info

        self.ex_type = ex_type
        self.ex_value = ex_value
        self.tb = tb

        self.user_triggered = str(ex_value) == "USER"

        self.setObjectName("ExceptionDialog")
        if self.user_triggered:
            self.setWindowTitle("User Bug Report")
        else:
            self.setWindowTitle("Critical Error")
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.media, "bug.png")))
        # noinspection PyArgumentList
        self.setMinimumSize(200, 200)
        # noinspection PyArgumentList
        self.resize(500, 300)

        self.main_layout = QtWidgets.QHBoxLayout(self)

        # left layout

        self.left_layout = QtWidgets.QVBoxLayout()
        self.icon_label = QtWidgets.QLabel(self)
        self.icon_label.setPixmap(os.path.abspath(os.path.join(self.media, "bug.png")))
        self.icon_label.setScaledContents(True)
        # noinspection PyArgumentList
        self.icon_label.setFixedSize(96, 96)
        self.left_layout.addWidget(self.icon_label)
        self.left_layout.addStretch()
        self.main_layout.addLayout(self.left_layout)

        # right layout

        self.right_layout = QtWidgets.QVBoxLayout()

        self.error_msg_label = QtWidgets.QLabel(self)
        self.error_msg_label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.error_msg_label.setWordWrap(True)
        self.error_msg_label.setOpenExternalLinks(True)
        self.error_msg_label.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse | QtCore.Qt.TextSelectableByMouse)
        self.right_layout.addWidget(self.error_msg_label)

        self.tb_groupbox = QtWidgets.QGroupBox(self)
        self.tb_groupbox.setCheckable(True)
        self.tb_groupbox.setObjectName("tracebackGroupBox")
        self.tb_layout = QtWidgets.QVBoxLayout(self.tb_groupbox)
        self.tb_editor = QtWidgets.QTextBrowser(self.tb_groupbox)
        self.tb_editor.setLineWrapMode(QtWidgets.QTextBrowser.NoWrap)
        self.tb_editor.setPlainText("")
        self.tb_editor.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard | QtCore.Qt.TextSelectableByMouse)
        self.tb_layout.addWidget(self.tb_editor)
        # noinspection PyUnresolvedReferences
        self.tb_groupbox.toggled[bool].connect(self.tb_editor.setVisible)
        self.right_layout.addWidget(self.tb_groupbox)
        if self.user_triggered:
            self.tb_editor.setReadOnly(False)
            logger.debug("editable-text mode")
        else:
            self.tb_editor.setReadOnly(True)

        self.text_label = QtWidgets.QLabel(self)
        text = "Please create a <a href=\"https://github.com/hydroffice/hyo2_openbst/issues\">bug report</a>" \
               " or write an email to <a href=\"mailto:%s\">%s</a>." \
               % (app_info.app_support_email, app_info.app_support_email)
        self.text_label.setWordWrap(True)
        self.text_label.setText(text)
        self.text_label.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse | QtCore.Qt.TextSelectableByMouse)
        # noinspection PyUnresolvedReferences
        self.text_label.linkActivated.connect(self.link_activated)
        self.right_layout.addWidget(self.text_label)

        self.right_layout.addSpacing(12)

        self.buttons_groupbox = QtWidgets.QDialogButtonBox(self)
        self.buttons_groupbox.setOrientation(QtCore.Qt.Horizontal)
        self.buttons_groupbox.setStandardButtons(QtWidgets.QDialogButtonBox.Close | QtWidgets.QDialogButtonBox.Ignore)
        self.right_layout.addWidget(self.buttons_groupbox)
        # noinspection PyUnresolvedReferences
        self.buttons_groupbox.accepted.connect(self.accept)
        # noinspection PyUnresolvedReferences
        self.buttons_groupbox.rejected.connect(self.reject)

        # noinspection PyArgumentList
        style = QtWidgets.QApplication.style()

        self.email_button = QtWidgets.QPushButton(style.standardIcon(style.SP_CommandLink), 'Email',
                                                  toolTip='Send the bug report via email.', autoDefault=False,
                                                  clicked=self.email_bug_report)
        self.buttons_groupbox.addButton(self.email_button, QtWidgets.QDialogButtonBox.ActionRole)

        self.save_button = QtWidgets.QPushButton(style.standardIcon(style.SP_DialogSaveButton), 'Save',
                                                 toolTip='Save the bug report on file.', autoDefault=False,
                                                 clicked=self.save_bug_report)
        self.buttons_groupbox.addButton(self.save_button, QtWidgets.QDialogButtonBox.ActionRole)

        self.right_layout.addStretch()

        self.main_layout.addLayout(self.right_layout)

        self._fill()

    def _fill(self):
        if self.user_triggered:
            self.error_msg = r"User-triggered bug report"
            self.traceback_editor = r"<Write here the bug description>"
            return

        if self.has_exception_info():
            lines = traceback.format_exception_only(self.ex_type, self.ex_value)
            msg = "\n".join(lines)
            logger.debug("msg: %s" % msg)
            self.error_msg = msg
            self.traceback_editor = self.tb
        else:
            self.error_msg = r"N\A"
            self.traceback_editor = r"N\A"

    # error message

    @property
    def error_msg(self) -> str:
        return self.error_msg_label.text()

    @error_msg.setter
    def error_msg(self, value: str) -> None:
        self.error_msg_label.setText(value)

    # traceback

    @property
    def traceback_editor(self) -> str:
        return self.tb_editor.document().toPlainText()

    @traceback_editor.setter
    def traceback_editor(self, value: Union[TracebackType, str]) -> None:
        if isinstance(value, TracebackType):
            value = "".join(traceback.format_tb(value))
        self.tb_editor.document().setPlainText(value)

    # text

    @property
    def text(self):
        return self.text_label.text()

    @text.setter
    def text(self, value: str):
        self.text_label.setText(value)

    # exception info

    @property
    def exception_info(self):
        return self.ex_type, self.ex_value, self.tb

    @exception_info.setter
    def exception_info(self, value: Sequence):
        if len(value) != 3:
            raise RuntimeError("invalid number of items: %d" % len(value))
        self.ex_type = value[0]
        self.ex_value = value[1]
        self.tb = value[2]
        self._fill()

    def has_exception_info(self) -> bool:
        return all((self.ex_type, self.ex_value, self.tb))

    def reset_exception_info(self) -> None:
        self.ex_type = None
        self.ex_value = None
        self.tb = None

    # reporting

    def format_bug_report(self):
        separator = "-" * 120 + "\n"
        timestamp = "%s v.%s - %s\n" % (self._ai.app_name, self._ai.app_version, email.utils.formatdate(localtime=True))

        msg = [timestamp, separator]
        msg.extend(traceback.format_exception_only(self.ex_type, self.ex_value))
        msg.append(separator)
        msg.append('Traceback:\n')
        if self.user_triggered:
            msg.extend(self.tb_editor.toPlainText() + "\n")
        else:
            msg.extend(traceback.format_tb(self.tb))
        msg.append(separator)
        msg.extend(Helper(lib_info=self._li).package_info().splitlines(True))
        msg[-1] = msg[-1] + '\n'
        msg.append(separator)

        return msg

    def email_bug_report(self):
        logger.debug("email bug report")

        error = traceback.format_exception_only(self.ex_type, self.ex_value)[-1].strip()
        if self.user_triggered:
            subject = "%s v.%s - User Bug Report - %.0f" \
                      % (self._ai.app_name, self._ai.app_version, datetime.utcnow().timestamp())
        else:
            subject = "%s v.%s - Bug Report - %.0f - %s" \
                      % (self._ai.app_name, self._ai.app_version, datetime.utcnow().timestamp(), error)

        body = "[Insert your comments here and/or attach any meaningful screenshots]\n\n"
        body += "-" * 120 + "\n"
        body += "-" * 120 + "\n"
        body += "".join(self.format_bug_report())

        url = QtCore.QUrl("mailto:%s <%s>" % (self._ai.app_support_email, self._ai.app_support_email))
        url_query = QtCore.QUrlQuery()
        url_query.addQueryItem("subject", subject)
        url_query.addQueryItem("body", body)
        url.setQuery(url_query)

        # noinspection PyCallByClass,PyArgumentList
        ret = QtGui.QDesktopServices.openUrl(url)
        if not ret:
            msg = "Issue in transmitting the bug report.\n" \
                  "Save the bug report on file and transmit it manually."
            # noinspection PyCallByClass,PyArgumentList
            QtWidgets.QMessageBox.warning(self, "Emailing Issue", msg)

    def save_bug_report(self):
        logger.debug("save bug report")

        report = "".join(self.format_bug_report())
        hint_name = "%s_%s_bug_%.0f" \
                    % (self._ai.app_name, self._ai.app_version.replace(".", "_"), datetime.utcnow().timestamp())
        # noinspection PyCallByClass
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Bug Report", hint_name,
                                                            "Text files (*.txt)", "Text files (*.txt)")
        if filename:
            fd = open(filename, 'w')
            try:
                fd.write(report)
                fd.close()
                Helper.explore_folder(filename)
            except Exception as e:
                msg = 'Unable to save the bug report:\n%s' % str(e)
                # noinspection PyCallByClass,PyArgumentList
                QtWidgets.QMessageBox.warning(self, "Saving issue", msg)

    def link_activated(self, url):
        if "mailto:" in url:
            self.email_bug_report()
        else:
            Helper.explore_folder(url)
