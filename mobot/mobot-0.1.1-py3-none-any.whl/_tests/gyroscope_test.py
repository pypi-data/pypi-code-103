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

class GyroscopeTestAgent(Agent):
    def __init__(self):
        Agent.__init__(self)
        self.gyroscope.register_callback(self.gyroscope_cb)

    def gyroscope_cb(self, w, metadata):
        wx = "{:.2f}".format(w[0])
        wy = "{:.2f}".format(w[1])
        wz = "{:.2f}".format(w[2])
        self.logger.info(f"wx: {wx}, wy: {wy}, wz: {wz}")

def main():
    gyroscope_test_agent = GyroscopeTestAgent()
    gyroscope_test_agent.start()

if __name__ == "__main__":
    main()
