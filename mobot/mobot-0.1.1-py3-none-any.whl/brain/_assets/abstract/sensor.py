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

from .asset import Asset

import mobot._proto.common_pb2 as common_pb2

class Sensor(Asset):
    def __init__(self, logger, connection):
        Asset.__init__(self, logger, connection)
        self.__metadata = None
        self.__callback_fn = None

    def _set_sensor_metadata(self, metadata, context):
        if self._is_body(context):
            self.__metadata = metadata
            return common_pb2.Success(success=True)
        else:
            return common_pb2.Success(success=False)

    def _new_sensor_data(self, raw_data, context):
        if self._is_body(context):
            data = self._format_data(raw_data)
            if self.__callback_fn != None:
                self.__callback_fn(data, self.__metadata)
            else:
                return common_pb2.Success(success=False)
            return common_pb2.Success(success=True)
        else:
            return common_pb2.Success(success=False)

    def register_callback(self, callback):
        self.__callback_fn = callback

    def _format_data(self, raw_data):
        pass
