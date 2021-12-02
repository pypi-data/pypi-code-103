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

class AccelerometerTestAgent(Agent):
    def __init__(self):
        Agent.__init__(self)
        self.accelerometer.register_callback(self.accelerometer_cb)

    def accelerometer_cb(self, a, metadata):
        ax = "{:.2f}".format(a[0])
        ay = "{:.2f}".format(a[1])
        az = "{:.2f}".format(a[2])
        self.logger.info(f"ax: {ax}, ay: {ay}, az: {az}")

def main():
    accelerometer_test_agent = AccelerometerTestAgent()
    accelerometer_test_agent.start()

if __name__ == "__main__":
    main()
