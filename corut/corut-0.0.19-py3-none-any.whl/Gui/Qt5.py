#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Easy functions have been developed by grouping frequently used operations with QT.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

import os
import sys
from PyQt5.QtCore import (
    QDateTime,
    QSize,
    QTime,
    QUrl,
    Qt,
    pyqtSignal,
    qFuzzyCompare
)
from PyQt5.QtGui import QColor, QFont, QIcon
from PyQt5.QtMultimedia import (
    QMediaContent,
    QMediaPlayer,
    QVideoProbe
)
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateTimeEdit,
    QDesktopWidget,
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSlider,
    QSplashScreen,
    QStyle,
    QTableView,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget
)
from time import sleep

SET_WORD_WRAP_STATUS = True
SET_FONT = QFont("Arial", 9, QFont.Normal)
SET_APP_NAME_TITLE = ''
SET_APP_ICON_PATH = None


# noinspection PyBroadException
def close_event(self):
    try:
        self.deleteLater()
    except Exception:
        pass
    try:
        self.close()
    except Exception:
        pass
    try:
        print(f'{self.__class__.__name__.upper()} exited successfully...')
    except Exception:
        pass


def colour_converter(data=None, item=None):
    if data in ('None', None):
        return QColor(Qt.yellow) if item is None else 'yellow'
    elif data in ('False', False):
        return QColor(Qt.red) if item is None else 'red'
    elif data in ('True', True):
        return QColor(Qt.green) if item is None else 'green'
    elif data == 'NULL':
        return QColor(255, 255, 255)
    else:
        return QColor(Qt.__dict__.get(data)) if item is None else data


def convert_ui_to_py(file_path):
    """
    It converts the UI file to py code. Extracts the UI file to the directory it is in
    :param file_path: The full path to the UI file must be entered.
    """
    pyuic5 = os.path.join(os.path.dirname(sys.executable), 'pyuic5')
    file_name = os.path.basename(file_path)[:-3]
    os.chdir(os.path.dirname(file_path))
    os.system(f"{pyuic5} {file_name}.ui -o {file_name}.py")


def set_global_font(font='Arial', size=9):
    global SET_FONT
    SET_FONT = QFont(font, size, QFont.Normal)
    return SET_FONT


def transaction_confirmation(self, title, message):
    reply = QMessageBox.question(
        self, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
    )
    if reply == QMessageBox.Yes:
        return True
    else:
        return False


# noinspection PyArgumentList,PyUnresolvedReferences
class _PlayerControls(QWidget):
    play = pyqtSignal()
    pause = pyqtSignal()
    stop = pyqtSignal()
    changeVolume = pyqtSignal(int)
    changeMuting = pyqtSignal(bool)
    changeRate = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.playerState = QMediaPlayer.StoppedState
        self.playerMuted = False

        self.playButton = QToolButton(clicked=self.clicked_play)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        self.stopButton = QToolButton(clicked=self.stop)
        self.stopButton.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stopButton.setEnabled(False)

        self.muteButton = QToolButton(clicked=self.clicked_mute)
        self.muteButton.setIcon(
            self.style().standardIcon(QStyle.SP_MediaVolume))

        self.volumeSlider = QSlider(Qt.Horizontal, sliderMoved=self.changeVolume)
        self.volumeSlider.setRange(0, 100)

        self.rateBox = QComboBox(activated=self.update_rate)
        self.rateBox.addItem("0.5x", 0.5)
        self.rateBox.addItem("1.0x", 1.0)
        self.rateBox.addItem("2.0x", 2.0)
        self.rateBox.addItem("4.0x", 4.0)
        self.rateBox.setCurrentIndex(1)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stopButton)
        layout.addWidget(self.playButton)
        layout.addWidget(self.muteButton)
        layout.addWidget(self.volumeSlider)
        layout.addWidget(self.rateBox)
        self.setLayout(layout)

    def state(self):
        return self.playerState

    def state_set(self, state):
        if state != self.playerState:
            self.playerState = state
            if state == QMediaPlayer.StoppedState:
                self.stopButton.setEnabled(False)
                self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            elif state == QMediaPlayer.PlayingState:
                self.stopButton.setEnabled(True)
                self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            elif state == QMediaPlayer.PausedState:
                self.stopButton.setEnabled(True)
                self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def volume(self):
        return self.volumeSlider.value()

    def volume_set(self, volume):
        self.volumeSlider.setValue(volume)

    def is_muted(self):
        return self.playerMuted

    def set_muted(self, muted):
        if muted != self.playerMuted:
            self.playerMuted = muted
            self.muteButton.setIcon(
                self.style().standardIcon(
                    QStyle.SP_MediaVolumeMuted if muted else QStyle.SP_MediaVolume)
            )

    def clicked_play(self):
        if self.playerState in (QMediaPlayer.StoppedState, QMediaPlayer.PausedState):
            self.play.emit()
        elif self.playerState == QMediaPlayer.PlayingState:
            self.pause.emit()

    def clicked_mute(self):
        self.changeMuting.emit(not self.playerMuted)

    def playback_rate(self):
        return self.rateBox.itemData(self.rateBox.currentIndex())

    def playback_rate_set(self, rate):
        for i in range(self.rateBox.count()):
            if qFuzzyCompare(rate, self.rateBox.itemData(i)):
                self.rateBox.setCurrentIndex(i)
                return
        self.rateBox.addItem("%dx" % rate, rate)
        self.rateBox.setCurrentIndex(self.rateBox.count() - 1)

    def update_rate(self):
        self.changeRate.emit(self.playback_rate())


class _VideoWidget(QVideoWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.setFullScreen(False)
            event.accept()
        elif event.key() == Qt.Key_Enter and event.modifiers() & Qt.Key_Alt:
            self.setFullScreen(not self.isFullScreen())
            event.accept()
        else:
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.setFullScreen(not self.isFullScreen())
        event.accept()


# noinspection PyUnresolvedReferences,PyArgumentList
class MediaPlayer(QWidget):
    fullScreenChanged = pyqtSignal(bool)

    def __init__(self, icon_path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowIcon(
            QIcon(icon_path if icon_path else SET_APP_ICON_PATH if SET_APP_ICON_PATH else None)
        )
        self.duration = 0
        self.player = QMediaPlayer()
        self.player.durationChanged.connect(self.changed_duration)
        self.player.positionChanged.connect(self.changed_position)
        self.player.videoAvailableChanged.connect(self.changed_video_available)
        self.video_widget = _VideoWidget()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, int(self.player.duration() / 1000))
        self.labelDuration = QLabel()
        self.slider.sliderMoved.connect(self.seek)
        self.probe = QVideoProbe()
        self.probe.setSource(self.player)
        controls = _PlayerControls()
        controls.state_set(self.player.state())
        controls.volume_set(self.player.volume())
        controls.set_muted(controls.is_muted())

        controls.play.connect(self.player.play)
        controls.pause.connect(self.player.pause)
        controls.stop.connect(self.player.stop)
        controls.changeVolume.connect(self.player.setVolume)
        controls.changeMuting.connect(self.player.setMuted)
        controls.changeRate.connect(self.player.setPlaybackRate)
        controls.stop.connect(self.video_widget.update)

        self.player.stateChanged.connect(controls.state_set)
        self.player.volumeChanged.connect(controls.volume_set)
        self.player.mutedChanged.connect(controls.set_muted)

        self.fullScreenButton = QPushButton("Full Screen")
        self.fullScreenButton.setCheckable(True)

        layout_video = QHBoxLayout()
        layout_video.setContentsMargins(0, 0, 0, 0)
        layout_video.addWidget(self.video_widget)

        layout_control = QGridLayout()
        layout_control.addWidget(self.slider, 1, 0)
        layout_control.addWidget(self.labelDuration, 1, 1)
        layout_control.addWidget(controls, 2, 0)
        layout_control.addWidget(self.fullScreenButton, 2, 1)

        grid = QGridLayout()
        grid.addLayout(layout_video, 1, 0)
        grid.addLayout(layout_control, 2, 0)

        self.setLayout(grid)
        self.player.setVideoOutput(self.video_widget)

        if not self.player.isAvailable():
            QMessageBox.warning(
                self,
                "Service not available",
                "The QMediaPlayer object does not have a valid service.\n"
                "Please check the media service plugins are installed."
            )
            controls.setEnabled(False)
            self.fullScreenButton.setEnabled(False)
        self.show()

    def load_file(self, file_path, name):
        if file_path is not None and os.path.exists(file_path):
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.player.play()
        self.setWindowTitle(f'{SET_APP_NAME_TITLE}Video Player ---> Content Name:{name}')
        self.resize(640, 480)

    def changed_duration(self, duration):
        duration /= 1000
        self.duration = duration
        self.slider.setMaximum(duration)

    def changed_position(self, progress):
        progress /= 1000
        if not self.slider.isSliderDown():
            self.slider.setValue(progress)
        self.update_duration_info(progress)

    def seek(self, seconds):
        self.player.setPosition(seconds * 1000)

    def handle_cursor(self, status):
        if status in (
                QMediaPlayer.LoadingMedia, QMediaPlayer.BufferingMedia, QMediaPlayer.StalledMedia
        ):
            self.setCursor(Qt.BusyCursor)
        else:
            self.unsetCursor()

    def changed_video_available(self, available):
        if available:
            self.fullScreenButton.clicked.connect(self.video_widget.setFullScreen)
            self.video_widget.fullScreenChanged.connect(self.fullScreenButton.setChecked)
            if self.fullScreenButton.isChecked():
                self.video_widget.setFullScreen(True)
        else:
            # noinspection PyBroadException
            try:
                self.fullScreenButton.clicked.disconnect(self.video_widget.setFullScreen)
                self.video_widget.fullScreenChanged.disconnect(self.fullScreenButton.setChecked)
            except Exception:
                pass
            self.video_widget.setFullScreen(False)

    def update_duration_info(self, info):
        duration = self.duration
        if info or duration:
            time_current = QTime((info / 3600) % 60, (info / 60) % 60, info % 60,
                                 (info * 1000) % 1000)
            time_total = QTime((duration / 3600) % 60, (duration / 60) % 60, duration % 60,
                               (duration * 1000) % 1000)
            time_format = 'hh:mm:ss' if duration > 3600 else 'mm:ss'
            time_to_str = time_current.toString(time_format) + " / " + time_total.toString(
                time_format)
        else:
            time_to_str = ""
        self.labelDuration.setText(time_to_str)
        if duration != 0 and info != 0 and duration == info:
            self.player.pause()
            self.player.stop()
            self.video_widget.update()
            print('Player Stopped...')

    def closeEvent(self, event):
        self.player.pause()
        self.player.stop()
        self.video_widget.update()
        self.player.disconnect()
        event.ignore()
        self.hide()
        close_event(self)


# noinspection PyArgumentList,PyUnresolvedReferences
class DialogLogin(QDialog):
    def __init__(
            self, username=None, password=None, title='Sign In', icon_path=None,
            windows_size=(240, 70)
    ):
        super().__init__(parent=None)
        self.__username = username
        self.__password = password
        self.setWindowTitle(title if title else SET_APP_NAME_TITLE if SET_APP_NAME_TITLE else None)
        self.setWindowIcon(
            QIcon(icon_path if icon_path else SET_APP_ICON_PATH if SET_APP_ICON_PATH else None)
        )
        self.ui_line_edit_user_name = QLineEdit()
        self.ui_line_edit_user_name.setClearButtonEnabled(True)
        self.ui_line_edit_user_name.setPlaceholderText("Enter Username")
        self.ui_line_edit_password = QLineEdit()
        self.ui_line_edit_password.setClearButtonEnabled(True)
        self.ui_line_edit_password.setPlaceholderText("Enter Password")
        self.ui_line_edit_password.setEchoMode(QLineEdit.Password)
        self.ui_push_button_login = QPushButton("Login")
        self.ui_push_button_exit = QPushButton("Exit")
        layout = QGridLayout()
        layout.addWidget(self.ui_line_edit_user_name, 0, 0, 1, 0)
        layout.addWidget(self.ui_line_edit_password, 1, 0, 1, 0)
        layout.addWidget(self.ui_push_button_login, 2, 0, 1, 1)
        layout.addWidget(self.ui_push_button_exit, 2, 1, 1, 1)
        self.setLayout(layout)
        self.ui_push_button_login.clicked.connect(self.handle_login)
        self.ui_push_button_exit.clicked.connect(self.handle_exit)
        self.setMinimumSize(QSize(*windows_size))

    def handle_login(self):
        if (
                self.ui_line_edit_user_name.text() == self.__username and
                self.ui_line_edit_password.text() == self.__password
        ):
            self.accept()
        else:
            QMessageBox.warning(self, 'Login Error!', 'Username or password is wrong.')

    def handle_exit(self):
        close_event(self)


class DialogWait(QSplashScreen):
    def __init__(
            self,
            message_size=(400, 200),
            font=("Arial Black", 21),
            background='background-color:red'
    ):
        super().__init__()
        self.setFont(QFont(*font, QFont.Bold))
        self.setStyleSheet(background)
        self.resize(*message_size)
        frame_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
        self.show()
        sleep(0.2)

    def show_message(
            self,
            message=f'{SET_APP_NAME_TITLE}Running\nPlease Wait ...',
            color=Qt.white,
            alignment=Qt.AlignCenter
    ):
        self.show()
        self.clearMessage()
        print(f'DialogWait ---> {message}')
        self.showMessage(message, color=color, alignment=alignment)
        self.show()


class SetQCheckBox(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)


class SetQComboBox(QComboBox):
    def __init__(self, data=None, items=None, colour=None, index_changed=None, parent=None):
        super().__init__(parent)
        if items:
            self.addItems(items)
        if data:
            self.setCurrentText(str(data))
        if index_changed:
            # noinspection PyUnresolvedReferences
            self.currentIndexChanged.connect(index_changed)
        self.setFont(SET_FONT)
        if colour:
            self.setStyleSheet(f"background-color:{colour_converter(colour, 'QComboBox')}")
        setattr(self, "get_all_items", lambda: [self.itemText(i) for i in range(self.count())])

    # noinspection PyUnresolvedReferences,PyBroadException
    def disconnect_changed(self, event='index'):
        try:
            if event.lower() == 'index':
                self.currentIndexChanged.disconnect()
            elif event.lower() == 'text':
                self.currentTextChanged.disconnect()
        except Exception:
            pass

    def clear_and_add_items(self, items, event='index', set_index_or_text=None):
        self.disconnect_changed(event=event)
        self.clear()
        if items and isinstance(items, list):
            self.addItems(items)
        if set_index_or_text:
            if event.lower() == 'index':
                self.setCurrentIndex(set_index_or_text)
            elif event.lower() == 'text':
                self.setCurrentText(set_index_or_text)

    def selectable_values_add(self, values):
        self.clear()
        for value in values:
            self.addItem(str(value))
            item = self.model().item(self.count() - 1, 0)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.TextEditable)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)

    def selectable_values_get(self):
        values = []
        for index in range(self.count()):
            item = self.model().item(index)
            if item.checkState() == Qt.Checked:
                values.append(self.itemText(index))
        return values


class SetQDateTimeEdit(QDateTimeEdit):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        if isinstance(data, str):
            # noinspection PyArgumentList
            self.setDateTime(QDateTime.fromString(data))
        else:
            self.setDateTime(data)


class SetQGroupBox(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)


class SetQLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, data, colour=None, parent=None):
        super().__init__(parent)
        self.setText(str(data))
        self.setIndent(4)
        self.setMargin(1)
        self.setWordWrap(SET_WORD_WRAP_STATUS)
        if colour:
            self.setStyleSheet(f"background-color:{colour_converter(colour, 'QLabel')}")
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)

    # noinspection PyUnresolvedReferences
    def mousePressEvent(self, event):
        self.clicked.emit()


class SetQLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)


class SetQMessageBox(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(SET_FONT)


class SetQPushButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)


class SetQTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def table_widget_clear(self):
        self.clear()
        self.setColumnCount(0)
        self.setRowCount(0)

    def table_widget_update(
            self, column_labels, data=None, old_sort_order=None, hide_columns=None,
            set_background_by_column_value=None
    ):
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(0)
        self.setColumnCount(len(column_labels))
        column_label_value = column_labels.copy()
        if isinstance(column_labels, dict):
            column_label_value = list(column_labels.values())
            column_labels = list(column_labels)
        self.setHorizontalHeaderLabels(column_labels)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSortingEnabled(False)
        self.verticalScrollBar().setSliderPosition(self.verticalScrollBar().minimum())
        if data:
            self.setRowCount(len(data))
            for index_row, lines in enumerate(data):
                for column, item in enumerate(lines):
                    if (
                            isinstance(column_label_value[column], type) and
                            str(column_label_value[column].__name__).startswith('SetQ')
                    ):
                        self.setCellWidget(index_row, column, item)
                    else:
                        if isinstance(item, int) or isinstance(item, float):
                            item_value = QTableWidgetItem()
                            item_value.setData(Qt.EditRole, item)
                        else:
                            item_value = QTableWidgetItem(str(item))
                        self.setItem(index_row, column, item_value)
                    if set_background_by_column_value:
                        self.item(index_row, column).setBackground(
                            colour_converter(lines[set_background_by_column_value])
                        )
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        if old_sort_order:
            self.sortItems(*old_sort_order)
        self.setSortingEnabled(True)
        if hide_columns:
            for column in (hide_columns if isinstance(hide_columns, list) else [hide_columns]):
                self.setColumnHidden(column, True)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def table_widget_get_all_data(self):
        rows = self.rowCount()
        columns = self.columnCount()
        data = []
        for row in range(rows):
            line = []
            for col in range(columns):
                line.extend([self.item(row, col).text()])
            data.extend([line])
        return data

    def get_multi_selected_values(self, columns, return_only_first_item=False):
        """
        Returns the value of one or more columns
        :type columns: If it is a column, it takes an int value.
                       List of column index is given for multiple columns
        :type return_only_first_item: if you want to return only the first item of the list
        :rtype: object
        """
        rows = []
        for selected_rows in self.selectionModel().selectedRows():
            if isinstance(columns, list):
                c = []
                for column in columns:
                    c.append(self.item(selected_rows.row(), column).text())
                rows.append(c)
            elif isinstance(columns, int):
                rows.append(self.item(selected_rows.row(), columns).text())
        return rows if not (return_only_first_item and rows) else rows[0]


class SetQTextEdit(QTextEdit):
    def __init__(self, data, colour=None, parent=None):
        super().__init__(parent)
        self.setText(str(data))
        self.setFont(SET_FONT)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.setLineWrapMode(QTextEdit.NoWrap)
        if colour:
            self.setStyleSheet(f"background-color:{colour_converter(colour, 'QTextEdit')}")


class SetQTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def create_baby_child(self, groups, details):
        self.clear()
        for group in groups:
            child = QTreeWidgetItem(self)
            child.setText(0, group)
            child.setFlags(child.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            child.setCheckState(0, False)
            for child_value_second, child_group_name, child_value_first, color_status in details:
                if child_group_name == group:
                    baby = QTreeWidgetItem(child)
                    baby.setFlags(baby.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                    baby.setText(0, child_value_first)
                    baby.setText(1, str(child_value_second))
                    baby.setCheckState(0, False)
                    baby.setBackground(0, colour_converter(color_status))
