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

from .abstract.sensor import Sensor

import mobot._proto.listen_pb2_grpc as pb2_grpc

class Listen(pb2_grpc.ListenServicer, Sensor):
    def __init__(self, logger, connection):
        Sensor.__init__(self, logger, connection)

    ## Private method (used for grpc communication)
    def SetListenMetadata(self, listen_metadata, context):
        return self._set_sensor_metadata(listen_metadata, context)

    ## Private method (used for grpc communication)
    def NewListenData(self, message, context):
        return self._new_sensor_data(message, context)

    def _format_data(self, message):
        return message.text
