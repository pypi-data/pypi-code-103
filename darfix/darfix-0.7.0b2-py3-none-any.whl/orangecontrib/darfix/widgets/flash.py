# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/


__authors__ = ["J. Garriga"]
__license__ = "MIT"
__date__ = "12/08/2019"


from Orange.widgets.widget import OWWidget, Input, Output


class FlashWidgetOW(OWWidget):

    """
    Widget that creates a new dataset from a given one, and copies its data.
    """

    name = "flash"
    icon = "icons/flash.svg"
    want_main_area = False

    # Inputs
    class Inputs:
        dataset = Input("dataset", tuple)

    # Outputs
    class Outputs:
        dataset = Output("dataset", tuple)

    def __init__(self):
        super().__init__()

    @Inputs.dataset
    def setDataset(self, _input):
        # Copy and send new dataset
        try:
            self.dataset, update = _input
            self.dataset[0]._updateDataset(self.dataset[0], self.dataset[1])
            self.Outputs.dataset.send(((self,) + self.dataset[1:], None))
        except Exception:
            self.Outputs.dataset.send(None)

    def _updateDataset(self, widget, dataset):
        self.Outputs.dataset.send(((self, dataset) + self.dataset[2:], widget))

    def setVisible(self, visible):
        pass
