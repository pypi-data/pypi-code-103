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

from mobot.brain.agent import Agent

class MagnetometerTestAgent(Agent):
    def __init__(self):
        Agent.__init__(self)
        self.magnetometer.register_callback(self.magnetometer_cb)

    def magnetometer_cb(self, q, metadata):
        x = "{:.2f}".format(q[0])
        y = "{:.2f}".format(q[1])
        z = "{:.2f}".format(q[2])
        w = "{:.2f}".format(q[3])
        self.logger.info(f"x: {x}, y: {y}, z: {z}, w: {w}")

def main():
    magnetometer_test_agent = MagnetometerTestAgent()
    magnetometer_test_agent.start()

if __name__ == "__main__":
    main()
