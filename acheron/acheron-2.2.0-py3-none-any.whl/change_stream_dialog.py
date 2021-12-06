import logging

from PySide2 import QtWidgets

from .ui_change_stream_dialog import Ui_ChangeStreamDialog

logger = logging.getLogger(__name__)


class ChangeStreamDialog(QtWidgets.QDialog, Ui_ChangeStreamDialog):
    def __init__(self, streams, channels, stream_list, parent=None):
        super().__init__(parent)

        self.streams = streams
        self.channels = channels

        if stream_list is True:
            self.stream_list = list(range(len(streams)))
        else:
            self.stream_list = stream_list

        self.check_boxes = {}  # by stream index

        self.setupUi(self)

        self.add_check_boxes()

    def add_check_boxes(self):
        d = {}  # key: min(channel index), value: check box

        for index, stream in enumerate(self.streams):
            check_box = QtWidgets.QCheckBox(self)
            check_box.setChecked(index in self.stream_list)
            self.check_boxes[index] = check_box

            stream_channels = stream.channel_index_list[:stream.channel_count]

            channel_names = []
            for ch_index in stream_channels:
                channel = self.channels[ch_index]
                channel_names.append(channel.name.decode("utf-8"))

            stream_text = "Stream {} ({})".format(index,
                                                  ", ".join(channel_names))

            check_box.setText(stream_text)

            d[min(stream_channels)] = check_box

        for ch_index in sorted(d.keys()):
            check_box = d[ch_index]
            self.verticalLayout.addWidget(check_box)

    def get_new_stream_list(self):
        all_true = True

        stream_list = []

        for index in sorted(self.check_boxes.keys()):
            check_box = self.check_boxes[index]
            if check_box.isChecked():
                stream_list.append(index)
            else:
                all_true = False

        if all_true:
            return True
        else:
            return stream_list
