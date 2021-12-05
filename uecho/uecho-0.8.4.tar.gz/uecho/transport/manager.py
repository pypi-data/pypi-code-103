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

from typing import Any, List
from .interface import Interface
from .multicast_server import MulticastServer
from .unicast_server import UnicastServer
from .server import Server
from ..protocol.message import Message


class Manager(object):

    servers: List[Server]
    __TID: int

    def __init__(self):
        self.servers = []
        self.__TID = 0

    def __next_TID(self) -> int:
        self.__TID += 1
        if 0xFF < self.__TID:
            self.__TID = 0
        return self.__TID

    @property
    def ifaddr(self) -> str:
        for server in self.servers:
            if isinstance(server, UnicastServer):
                return self.ifaddr
        return ""

    @property
    def port(self) -> int:
        for server in self.servers:
            if isinstance(server, UnicastServer):
                return self.port
        return 0

    def add_observer(self, observer):
        for server in self.servers:
            server.add_observer(observer)

    def notify(self, msg: Message):
        for server in self.servers:
            server.notify(msg)

    def announce_message(self, msg: Message) -> bool:
        msg.TID = self.__next_TID()
        for server in self.servers:
            if isinstance(server, UnicastServer):
                server.announce_message(msg)
        return True

    def send_message(self, msg: Message, addr) -> bool:
        msg.TID = self.__next_TID()
        for server in self.servers:
            # TODO: Select an appropriate server from the specified address
            if isinstance(server, UnicastServer):
                if server.send_message(msg, addr):
                    return True
        return False

    def start(self, ifaddrs: List[str] = []) -> Any:
        if not self.stop():
            return False

        if len(ifaddrs) <= 0:
            ifaddrs = Interface.get_all_ipaddrs()
        for ifaddr in ifaddrs:
            userver = UnicastServer()
            if not userver.bind(ifaddr):
                self.stop()
                return False
            if not userver.start():
                self.stop()
                return False
            self.servers.append(userver)

            mserver = MulticastServer()
            if not mserver.bind(ifaddr):
                self.stop()
                return False
            if not mserver.start():
                self.stop()
                return False
            self.servers.append(mserver)

        if len(self.servers) <= 0:
            return False

        return True

    def stop(self) -> Any:
        for server in self.servers:
            server.stop()
        self.servers = []
        return True
