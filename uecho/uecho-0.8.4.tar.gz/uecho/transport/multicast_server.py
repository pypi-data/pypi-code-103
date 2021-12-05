# Copyright (C) 2021 Satoshi Konno. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import socket
from .server import Server


class MulticastServer(Server):
    ADDRESS = '224.0.23.0'

    def __init__(self):
        super().__init__()

    def bind(self, ifaddr: str) -> bool:
        if not super().bind(ifaddr):
            return False
        self.sock = self.create_udp_socket()
        self.sock.bind(('0.0.0.0', self.port))
        opt = socket.inet_aton(MulticastServer.ADDRESS) + socket.inet_aton(ifaddr)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, opt)
        return True
