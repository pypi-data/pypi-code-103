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
import threading
import grpc

import mobot._proto.common_pb2 as common_pb2
import mobot._proto.connection_pb2 as pb2
import mobot._proto.connection_pb2_grpc as pb2_grpc

class Resource:
    def __init__(self, uri):
        self.uri = uri
        self.lock = threading.Lock()
        self.lock.acquire()
        self.active = True

class Connection(pb2_grpc.ConnectionServicer):
    def __init__(self, logger):
        self.logger = logger
        self.body = None
        self.brain = None

    ## Private method (used for grpc communication)
    def Ping(self, _, context):
        return common_pb2.Empty()

    ## Private method (used for grpc communication)
    def AttachBodyStream(self, _, context):
        ########################## Remember the Body ###########################
        if self.body != None:
            error_msg = f"Attach Body request from \"{context.peer()}\" rejected as body at \"{self.body.uri}\" is attached!"
            self.logger.error(error_msg)
            context.cancel()
            return
        else:
            self.body = Resource(pb2.URI(uri = context.peer()))
            self.logger.info(f"Body at \"{self.body.uri.uri}\" attached!")
        ########################################################################

        is_active_thread = threading.Thread(target=self.poll_is_active, args=(context, self.body))
        is_active_thread.start()
        try:
            if self.brain!= None:
                self.brain.lock.release()
            while True:
                self.body.lock.acquire()
                if self.body.active:
                    yield self.brain.uri
                else:
                    raise grpc.RpcError
        except grpc.RpcError:
            self.body = None
            self.logger.info(f"Body detached!")

    ## Private method (used for grpc communication)
    def AttachBrainStream(self, _, context):
        ########################## Remember the Body ###########################
        if self.brain != None:
            error_msg = f"Attach Brain request from \"{context.peer()}\" rejected as brain at \"{self.brain.uri}\" is attached!"
            self.logger.error(error_msg)
            context.cancel()
            return
        else:
            brain_uri = ':'.join(context.peer().split(':')[:2]) + ':50052'
            self.brain = Resource(pb2.URI(uri = brain_uri))
            self.logger.info(f"Brain at \"{self.brain.uri.uri}\" attached!")
        ########################################################################

        is_active_thread = threading.Thread(target=self.poll_is_active, args=(context, self.brain))
        is_active_thread.start()
        try:
            if self.body!= None:
                self.brain.lock.release()
            while True:
                self.brain.lock.acquire()
                if self.brain.active:
                    yield self.body.uri
                    self.body.lock.release()
                else:
                    raise grpc.RpcError
        except grpc.RpcError:
            self.brain = None
            self.logger.info(f"Brain detached!")

    def poll_is_active(self, context, resource):
        while context.is_active():
            time.sleep(0.02)
        resource.active = False
        resource.lock.release()
