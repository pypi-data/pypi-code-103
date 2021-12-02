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

import time
import collections
import numpy as np
import threading
import curses
import texttable

from mobot.brain.agent import Agent
from mobot.utils.rate import Rate

class HzEstimator:
    def __init__(self, history_len, source_name=""):
        self.source_name = source_name
        self.pings = collections.deque(maxlen=history_len)
        self.hz_mean = 0.0
        self.hz_std = 0.0
        self.hz_min = 0.0
        self.hz_max = 0.0

    def ping(self):
        self.pings.append(time.time())
        self.update()

    def update(self):
        pings = np.array(self.pings)
        n_pings = len(pings)
        if n_pings < 2:
            return

        dts = pings[1:n_pings] - pings[0:n_pings-1]
        hzs = 1/dts
        self.hz_mean = np.mean(hzs)
        self.hz_std = np.std(hzs)
        self.hz_min = np.min(hzs)
        self.hz_max = np.max(hzs)

class PerformanceTestAgent(Agent):
    def __init__(self):
        Agent.__init__(self)
        self.accelerometer.register_callback(self.accelerometer_cb)
        self.gyroscope.register_callback(self.gyroscope_cb)
        self.magnetometer.register_callback(self.magnetometer_cb)
        self.camera.register_callback(self.camera_cb)

        self.chassis.enable()
        self.control_thread = threading.Thread(target=self.control_thread)

        self.perf_disp_thread = threading.Thread(target=self.perf_disp_thread)

        self.a_hz_ets = HzEstimator(200, source_name="Accelerometer")
        self.g_hz_ets = HzEstimator(200, source_name="Gyroscope")
        self.m_hz_ets = HzEstimator(200, source_name="Magnetometer")
        self.c_hz_ets = HzEstimator(100, source_name="Camera")
        self.ch_hz_ets = HzEstimator(100, source_name="Chassis")

    def on_start(self):
        self.perf_disp_thread.start()
        self.control_thread.start()

    def perf_disp_thread(self):
        stdscr = curses.initscr()
        curses.curs_set(0)
        curses.wrapper(self.perf_disp)

    def perf_disp(self, stdscr):
        rate = Rate(10)
        title = "Performance Test"
        while self.ok():
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            tableObj = texttable.Texttable()
            tableObj.set_cols_dtype(["t", "f", "f", "f", "f", "f"])
            tableObj.set_cols_align(["l", "c", "c", "c", "c", "c"])
            tableObj.set_cols_valign(["m", "m", "m", "m", "m", "m"])
            tableObj.add_rows([
                ["Hz", "Accelerometer", "Gyroscope", "Magnetometer", "Camera", "Chassis (Target=30Hz)"],
                ["Mean", self.a_hz_ets.hz_mean, self.g_hz_ets.hz_mean, self.m_hz_ets.hz_mean, self.c_hz_ets.hz_mean, self.ch_hz_ets.hz_mean],
                ["Std", self.a_hz_ets.hz_std, self.g_hz_ets.hz_std, self.m_hz_ets.hz_std, self.c_hz_ets.hz_std, self.ch_hz_ets.hz_std],
                ["Min", self.a_hz_ets.hz_min, self.g_hz_ets.hz_min, self.m_hz_ets.hz_min, self.c_hz_ets.hz_min, self.ch_hz_ets.hz_min],
                ["Max", self.a_hz_ets.hz_max, self.g_hz_ets.hz_max, self.m_hz_ets.hz_max, self.c_hz_ets.hz_max, self.ch_hz_ets.hz_max],
            ])
            table = tableObj.draw().split("\n")

            table_width = len(table[0])
            table_height = len(table)

            start_x_table = max(int((width // 2) - (table_width // 2) - table_width % 2), 0)
            start_y_table = max(int((height // 2) - (table_height // 2) - table_height % 2), 0)

            # Render Table
            for i, row in enumerate(table):
                if start_y_table + i == height - 1:
                    break
                stdscr.addstr(start_y_table + i, start_x_table, row[:width-1])

            statusbar = "Press ctrl + c to exit"
            stdscr.addstr(height-1, 0, statusbar[:width-1])

            stdscr.refresh()
            rate.sleep()


    def control_thread(self):
        rate = Rate(30)
        while self.ok():
            self.chassis.set_cmdvel(v=0.0, w=0.0)
            self.ch_hz_ets.ping()
            rate.sleep()

    def accelerometer_cb(self, a, metadata):
        self.a_hz_ets.ping()

    def gyroscope_cb(self, w, metadata):
        self.g_hz_ets.ping()

    def magnetometer_cb(self, q, metadata):
        self.m_hz_ets.ping()

    def camera_cb(self, image, metadata):
        self.c_hz_ets.ping()

def main():
    performance_test_agent = PerformanceTestAgent()
    performance_test_agent.start()

if __name__ == "__main__":
    main()
