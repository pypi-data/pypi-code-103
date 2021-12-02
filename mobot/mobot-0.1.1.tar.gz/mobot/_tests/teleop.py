# MIT License
#
# Copyright (c) 2021 Mobotx
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import threading
import numpy as np

from mobot.brain.agent import Agent
from mobot.utils.terminal import get_key, CTRL_PLUS_C
from mobot.utils.rate import Rate
from mobot.utils.joystick import Joystick

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class TeleopAgent(Agent):
    def __init__(self, ui):
        Agent.__init__(self)
        self.ui = ui
        self.camera.register_callback(self.camera_cb)
        self.flashlight.enable()
        self.chassis.enable()
        self.keyboard_teleop_thread = threading.Thread(target=self.keyboard_teleop_thread)
        self.control_thread = threading.Thread(target=self.control_thread)

        self.cmd_v = 0.0
        self.cmd_w = 0.0

    def on_start(self):
        self.keyboard_teleop_thread.start()
        self.control_thread.start()
        self.ui.flashlight.toggled.connect(self.flashlight_cb)
        self.ui.joystick.pose.connect(self.joystick_cb)

    def flashlight_cb(self):
        self.flashlight.toggle()

    def joystick_cb(self, x, y):
        wmax = (self.chassis.wheel_diameter * self.chassis.max_wheel_speed)/self.chassis.wheel_to_wheel_separation
        vmax = (self.chassis.wheel_diameter * self.chassis.max_wheel_speed)/2
        self.cmd_v = -(y/100) * vmax
        self.cmd_w = -(x/100) * wmax

    def keyboard_teleop_thread(self):
        self.bindings = {'w':( 0.07,  0.0),\
                         'a':( 0.0,  0.5),\
                         's':(-0.07,  0.0),\
                         'd':( 0.0, -0.5),\
                         ' ':( 0.0,  0.0)}
        self.help_msg = """
        Moving around:
                w
           a    s    d

        Spacebar to Stop!
        CTRL-C to quit
        """
        self.logger.info(self.help_msg)
        rate = Rate(50)
        while self.ok():
            key = get_key(0.1)
            if key in self.bindings:
                self.cmd_v=self.bindings[key][0]
                self.cmd_w=self.bindings[key][1]
            rate.sleep()
        print() ## Temp Fix for indentation in terminal

    def control_thread(self):
        rate = Rate(10)
        while self.ok():
            self.chassis.set_cmdvel(v=self.cmd_v, w=self.cmd_w)
            rate.sleep()

    def camera_cb(self, image, metadata):
        self.ui.set_image(image)

class Ui:
    def setupUi(self, main_window):
        main_window.setWindowTitle("Dashboard")
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.image = QLabel()
        self.flashlight = QCheckBox("Flashlight")
        self.flashlight.setChecked(False)
        self.joystick = Joystick()

        layout.addWidget(self.image)
        layout.addWidget(self.flashlight)
        layout.addWidget(self.joystick)
        central_widget.setLayout(layout)
        main_window.setCentralWidget(central_widget)

    def set_image(self, image):
        H, W, C = image.shape
        qImg = QImage(np.require(image, np.uint8, 'C'),
                W, H,
                QImage.Format_RGB888)

        pixmap = QPixmap(qImg)
        pixmap = pixmap.scaled(400,400, Qt.KeepAspectRatio)
        self.image.setPixmap(pixmap)

def main():
    app = QApplication([])
    app.setStyle(QStyleFactory.create("Cleanlooks"))
    main_window = QMainWindow()
    ui = Ui()
    ui.setupUi(main_window)
    teleop_agent = TeleopAgent(ui)
    main_window.show()
    teleop_agent.start()
    if not app.exec():
        teleop_agent.terminate()

if __name__ == "__main__":
    main()
