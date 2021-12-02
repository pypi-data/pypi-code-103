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

import grpc
import threading, time

from .asset import Asset

class Actuator(Asset):
    def __init__(self, logger, connection):
        Asset.__init__(self, logger, connection)

        self.available = False
        self.latency = 0.0
        self.__cmd = None

        self.__lock = threading.Lock()
        self.__new_cmd_lock = threading.Lock()
        self.__new_cmd_lock.acquire()
        self.__enabled = False

    def _actuator_cmd_stream(self, metadata, context):
        if self._is_body(context) and self.__enabled:
            self.__lock.acquire()
            self._set_metadata(metadata)
            self.available = True
            is_available_thread = threading.Thread(target=self.__poll_is_available, args=(context,))
            is_available_thread.start()
            try:
                while True:
                    self.__lock.acquire()
                    if self.available:
                        yield self.__cmd
                        if self.__new_cmd_lock.locked():
                            self.__new_cmd_lock.release()
                    else:
                        raise grpc.RpcError
            except grpc.RpcError:
                self.available = False
                self.__cmd = None
                self._reset_metadata()
                self.__lock.release()
        else:
            context.cancel()

    def __poll_is_available(self, context):
        while context.is_active():
            time.sleep(0.1)
        self.available = False
        self.__lock.release()

    def _new_cmd(self, cmd, blocking=False):
        if self.__lock.locked():
            self.__cmd = cmd
            if blocking:
                self.__lock.release()
                self.__new_cmd_lock.acquire()
            else:
                self.__lock.release()

    def enable(self):
        self.__enabled = True

    def _is_enabled(self):
        return self.__enabled

    def wait_until_available(self):
        while not self.available:
            time.sleep(0.1)
            if not self._connection.attach_brain_iterator.is_active():
                return False
        return True

    def _set_metadata(self, metadata):
        pass

    def _reset_metadata(self):
        pass
