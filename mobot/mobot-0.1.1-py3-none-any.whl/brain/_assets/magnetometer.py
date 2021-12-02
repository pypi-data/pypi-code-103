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

import numpy as np

from .abstract.sensor import Sensor

import mobot._proto.magnetometer_pb2_grpc as pb2_grpc

class Magnetometer(pb2_grpc.MagnetometerServicer, Sensor):
    def __init__(self, logger, connection):
        Sensor.__init__(self, logger, connection)

    ## Private method (used for grpc communication)
    def SetMagnetometerMetadata(self, magnetometer_metadata, context):
        return self._set_sensor_metadata(magnetometer_metadata, context)

    ## Private method (used for grpc communication)
    def NewMagnetometerData(self, orientation, context):
        return self._new_sensor_data(orientation, context)

    def _format_data(self, orientation):
        return np.array([orientation.x,\
            orientation.y,\
            orientation.z,\
            orientation.w])
