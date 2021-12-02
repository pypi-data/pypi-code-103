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

from concurrent import futures
import grpc

import mobot._proto.connection_pb2_grpc as pb2_grpc

from .connection import Connection
from mobot.utils.network import _get_ip_address
from mobot.utils.logging import _get_logger

def main():
    logger = _get_logger()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=30))
    pb2_grpc.add_ConnectionServicer_to_server(Connection(logger), server)

    try:
        ip = _get_ip_address()
    except:
        logger.error("Not Connected to any network!")
        return
    port = '50051'
    server.add_insecure_port(f'{ip}:{port}')

    server.start()
    logger.info(f"Mobot Spine started at \"{ip}:{port}\"")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)
