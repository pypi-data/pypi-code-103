#!/usr/bin/env python3
import signal
import sys
from functools import partial

from fime.config import Config
from fime.worklog import WorklogDialog

try:
    from PySide6 import QtCore, QtWidgets
    PYSIDE_6 = True
except ImportError:
    from PySide2 import QtCore, QtWidgets
    PYSIDE_6 = False

from fime.data import Tasks, Log, Data, LogCommentsData, Worklog, Report
from fime.exceptions import FimeException
from fime.import_task import ImportTask
from fime.report import ReportDialog
from fime.task_edit import TaskEdit
from fime.util import get_screen_height, get_icon


class App:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        data = Data()
        self.tasks = Tasks(data)
        lcd = LogCommentsData(data)
        self.log = Log(lcd)
        self._active_task = self.log.last_log() or "Nothing"

        config = Config()
        if config.tray_theme == "light":
            icon = get_icon("appointment-new-light")
        else:
            icon = get_icon("appointment-new")

        self.menu = QtWidgets.QMenu(None)

        self.import_task = ImportTask(config, None)
        self.import_task.accepted.connect(self.new_task_imported)

        self.taskEdit = TaskEdit(None)
        self.taskEdit.accepted.connect(self.tasks_edited)

        self.reportDialog = ReportDialog(self.tasks, Report(lcd), None)
        self.reportDialog.accepted.connect(self.log_edited)

        self.worklogDialog = WorklogDialog(config, Worklog(lcd), None)
        self.worklogDialog.accepted.connect(self.log_edited)

        self.tray = QtWidgets.QSystemTrayIcon()
        self.tray.setIcon(icon)
        self.tray.setContextMenu(self.menu)
        self.tray.show()
        self.tray.setToolTip("fime")
        self.update_tray_menu()

    @QtCore.Slot()
    def new_task_imported(self):
        if self.import_task.task_text:
            self.tasks.add_jira_task(self.import_task.task_text)
            self.update_tray_menu()

    @QtCore.Slot()
    def tasks_edited(self):
        self.tasks.tasks = self.taskEdit.tasks
        self.update_tray_menu()

    @QtCore.Slot()
    def log_edited(self):
        self.active_task = self.log.last_log() or "Nothing"

    @property
    def active_task(self):
        return self._active_task

    @active_task.setter
    def active_task(self, task):
        self._active_task = task
        self.tasks.update_jira_task_usage(self._active_task)
        self.update_tray_menu()

    def change_task(self, task):
        self.active_task = task
        self.log.log(task)

    def update_tray_menu(self):
        def add_tasks(tasks):
            for t in tasks:
                action = self.menu.addAction(t)
                action.triggered.connect(partial(self.change_task, t))
                if t == self.active_task:
                    action.setIcon(get_icon("go-next"))

        tmp_action = self.menu.addAction("tmp")
        action_height = self.menu.actionGeometry(tmp_action).height()

        self.menu.clear()
        add_tasks(self.tasks.tasks)

        self.menu.addSeparator()
        already_taken = (len(self.tasks.tasks) + 4) * action_height
        available_space = get_screen_height(self.menu) * 0.8 - already_taken
        jira_entry_count = int(available_space // action_height)
        add_tasks(self.tasks.jira_tasks[:jira_entry_count])

        self.menu.addSeparator()
        add_tasks(["Pause"])
        if self.active_task == "Nothing":
            add_tasks(["Nothing"])

        self.menu.addSeparator()

        new_action = self.menu.addAction("Import Jira task")
        new_action.triggered.connect(self.import_task.show)

        edit_action = self.menu.addAction("Edit tasks")
        edit_action.triggered.connect(self.edit_tasks)

        report_action = self.menu.addAction("Report")
        report_action.triggered.connect(self.reportDialog.show)

        worklog_action = self.menu.addAction("Worklog")
        worklog_action.triggered.connect(self.worklogDialog.show)

        self.menu.addSeparator()

        exit_action = self.menu.addAction("Close")
        exit_action.triggered.connect(self.app.quit)

    def sigterm_handler(self, signo, _frame):
        print(f'handling signal "{signal.strsignal(signo)}"')
        self.app.quit()

    def run(self):
        timer = QtCore.QTimer(None)
        # interrupt event loop regularly for signal handling
        timer.timeout.connect(lambda: None)
        timer.start(500)
        signal.signal(signal.SIGTERM, self.sigterm_handler)
        signal.signal(signal.SIGINT, self.sigterm_handler)
        if PYSIDE_6:
            self.app.exec()
        else:
            self.app.exec_()

    @QtCore.Slot()
    def edit_tasks(self):
        self.taskEdit.tasks = self.tasks.tasks
        self.taskEdit.show()


def excepthook(original, e_type, e_value, tb_obj):
    if e_type is FimeException:
        QtWidgets.QMessageBox.critical(None, "Error", str(e_value), QtWidgets.QMessageBox.Ok)
    else:
        original(e_type, e_value, tb_obj)


def main():
    # important for QStandardPath to be correct
    QtCore.QCoreApplication.setApplicationName("fime")
    # also catches exceptions in other threads
    original_excepthook = sys.excepthook
    sys.excepthook = partial(excepthook, original_excepthook)
    app = App()
    app.run()


if __name__ == "__main__":
    main()
