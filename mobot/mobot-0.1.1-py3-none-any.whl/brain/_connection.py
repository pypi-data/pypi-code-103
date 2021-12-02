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
import threading
import sys, signal

import mobot._proto.common_pb2 as common_pb2
import mobot._proto.connection_pb2_grpc as pb2_grpc

class Connection:
    def __init__(self, ip, logger):
        self.logger = logger

        self.channel = grpc.insecure_channel(f'{ip}:50051')
        self.stub = pb2_grpc.ConnectionStub(self.channel)

        self.attach_brain_iterator = None
        self.attach_brain_thread = None

        self._body_uri = None

    def attach(self):
        try:
            self.stub.Ping(common_pb2.Empty())
        except grpc.RpcError:
            self.logger.error("Unable to attach Brain to Spine!")
            sys.exit()
        self.attach_brain_iterator =  self.stub.AttachBrainStream(common_pb2.Empty())
        self.logger.info("Brain attched to Spine!")
        self.attach_brain_thread = threading.Thread(target=self.attach_thread)
        self.attach_brain_thread.start()

    def attach_thread(self):
        try:
            self.logger.info(f"Waiting for Body to be attached to spine...")
            for body in self.attach_brain_iterator:
                self.logger.info(f"Body at {body.uri} attached to spine")
                self._body_uri = body.uri
        except grpc.RpcError:
            self.logger.error("Brain detached from spine!")
            signal.alarm(0)

    def detach(self):
        if self.attach_brain_iterator != None:
            self.attach_brain_iterator.cancel()
