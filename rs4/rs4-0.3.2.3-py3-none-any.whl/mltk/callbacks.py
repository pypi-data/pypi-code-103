from tensorflow.keras.callbacks import Callback
import numpy as np
from rs4.termcolor import tc, stty_size

def confusion_matrix (labels, predictions, num_labels):
    rows = []
    for i in range (num_labels):
        row = np.bincount (predictions[labels == i], minlength=num_labels)
        rows.append (row)
    return np.vstack (rows)


class ConfusionMtrixCallback (Callback):
    def __init__(self, labels, validation_data, display_list = None):
        super().__init__()
        if not isinstance (labels, (list, tuple)):
            labels = [labels]
        self.labels = labels
        self.display_list = display_list
        self.xs, self.ys, self.logits = None, None, None
        self.validation_data = validation_data

    def _get_confusion_matrix (self, logits, ys):
        if logits is None:
            logits = self.logits
        if ys is None:
            ys = self.ys
        mat_ = confusion_matrix (
            np.argmax (logits, 1),
            np.argmax (ys, 1),
            logits.shape [1]
        )
        return mat_.T

    def _confusion_matrix (self, label_index = 0, indent = 8, show_label = True):
        cur_label = self.labels [label_index]
        if isinstance (self.ys, dict):
            ys = self.ys [self.model.outputs [label_index].name.split (":") [0].split ("/") [0]]
            logits = self.logits [label_index]
        else:
            ys = self.ys
            logits = self.logits
        mat_ = self._get_confusion_matrix (logits, ys)
        mat = str (mat_) [1:-1]

        try:
            print ("\nConfusion matrix{}, sensitivity: {:.4f}, specificity: {:.4f}"
                .format (
                    tc.info (cur_label.name and (" of " + cur_label.name) or ""),
                    mat_[0, 0] / (mat_[0, 1] + mat_[0, 0]),
                    mat_[1, 1] / (mat_[1, 1] + mat_[1, 0])
                )
            )
        except IndexError:
            return

        labels = []
        if show_label:
            first_row_length = len (mat.split ("\n", 1) [0]) - 2
            label_width = (first_row_length - 1) // mat_.shape [-1]
            labels = [str (each) [:label_width].rjust (label_width) for each in cur_label.class_names ()]
            print (tc.fail ((" " * (indent + label_width + 1)) + " ".join (labels)))

        lines = []
        for idx, line in enumerate (mat.split ("\n")):
            if idx > 0:
                line = line [1:]
            line = line [1:-1]
            if labels:
                line = tc.info (labels [idx]) + " " + line
            if indent:
                line = (" " * indent) + line
            print (line)

    def on_epoch_end(self, epoch, logs):
        self.xs, self.ys = self.validation_data
        self.logits = self.model.predict (self.xs)

        for label_index, label in enumerate (self.labels):
            if self.display_list and label.name not in self.display_list:
                continue
            self._confusion_matrix (label_index)

        columns, _ = stty_size ()
        print (tc.grey ('_' * columns + '\n'))

