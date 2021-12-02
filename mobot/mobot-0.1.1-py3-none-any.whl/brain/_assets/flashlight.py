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

from .abstract.actuator import Actuator

import mobot._proto.flashlight_pb2 as pb2
import mobot._proto.flashlight_pb2_grpc as pb2_grpc

class Flashlight(pb2_grpc.FlashlightServicer, Actuator):
    def __init__(self, logger, connection):
        Actuator.__init__(self, logger, connection)
        self.__on = False

    ## Private method (used for grpc communication)
    def FlashlightCmdStream(self, flashlight_metadata, context):
        for cmd in self._actuator_cmd_stream(flashlight_metadata, context):
            yield cmd

    def turn_on(self):
        success = self.__change_state(True)
        if success:
            self.__on = True
        return success

    def is_on(self):
        return self.__on

    def turn_off(self):
        success = self.__change_state(False)
        if success:
            self.__on = False
        return success

    def toggle(self):
        if self.__on:
            return self.turn_off()
        else:
            return self.turn_on()

    def __change_state(self, state):
        if self.available:
            self._new_cmd(pb2.FlashlightState(on=state))
        return self.available
