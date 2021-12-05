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

import time
import abc
from typing import Any, Union, List, Tuple, Optional

from .object import Object
from .transport.observer import Observer
from .local_node import LocalNode
from .node_profile import NodeProfile
from .esv import ESV
from .message import Message
from .protocol.message import Message as ProtocolMessage
from .property import Property
from .remote_node import RemoteNode
from .node import Node
from .manufacturer import Manufacture
from .std import Database
from .const import DEFAULT_POST_MSG_RERTY, DEFAULT_POST_MSG_WAIT


class ControleListener(metaclass=abc.ABCMeta):
    """ControleListener is an abstract listener class to listen to response and announce messages for nodes.
    """

    @abc.abstractmethod
    def node_add(self, node: RemoteNode):
        pass

    @abc.abstractmethod
    def node_updated(self, node: RemoteNode):
        pass


class Controller(Observer):
    """The Controller and find any devices of Echonet Lite,
    send any requests to the found devices and receive the responses
    easily without building the binary protocol messages directly.
    """

    class __PostMessage():

        request: Optional[Message]
        response: Optional[Message]

        def __init__(self):
            self.request = None
            self.response = None

        def is_waiting(self):
            if self.request is None:
                return False
            if self.response is not None:
                return False
            return True

    class __SearchMessage(Message):

        def __init__(self):
            super().__init__()
            self.ESV = ESV.READ_REQUEST
            self.SEOJ = NodeProfile.CODE
            self.DEOJ = NodeProfile.CODE
            prop = Property()
            prop.code = NodeProfile.CLASS_SELF_NODE_INSTANCE_LIST_S
            prop.data = bytearray()
            self.add_property(prop)

    __node: LocalNode
    __found_nodes: dict
    __last_post_msg: Any    # Controller.__PostMessage
    __database: Database
    __listeners: List[ControleListener]

    def __init__(self):
        self.__node = LocalNode()
        self.__found_nodes = {}
        self.__last_post_msg = Controller.__PostMessage()
        self.__database = Database()
        self.__listeners = []

    @property
    def nodes(self) -> List[RemoteNode]:
        """Retures found nodes.

        Returns:
            List[RemoteNode]; The found remote node list.
        """
        nodes = []
        for node in self.__found_nodes.values():
            nodes.append(node)
        return nodes

    def add_listener(self, listener: ControleListener):
        """Adds a listener to listen to response and announce messages for nodes.

        Args:
            listener (ControleListener): A listener implemented abstract methods of ControleListener.
        """
        self.__listeners.append(listener)

    def remove_listener(self, listener: ControleListener):
        """Removes the specified listener.

        Args:
            listener (ControleListener): The listener which is already added.
        """
        self.__listeners.remove(listener)

    def __notify_node_added(self, node: RemoteNode):
        for listener in self.__listeners:
            listener.node_add(node)

    def __notify_node_updated(self, node: RemoteNode):
        for listener in self.__listeners:
            listener.node_add(node)

    def get_standard_manufacturer(self, code: Union[int, bytes]) -> Optional[Manufacture]:
        return self.__database.get_manufacturer(code)

    def get_standard_manufacturer_name(self, code: Union[int, bytes]) -> Optional[str]:
        return self.__database.get_manufacturer_name(code)

    def get_standard_object(self, code: Union[Object, int, Tuple[int, int]]) -> Optional[Object]:
        return self.__database.get_object(code)

    def __is_node_profile_message(self, msg: ProtocolMessage):
        if msg.ESV != ESV.NOTIFICATION and msg.ESV != ESV.READ_RESPONSE:
            return False
        if msg.DEOJ != NodeProfile.CODE and msg.DEOJ != NodeProfile.CODE_READ_ONLY:
            return False
        return True

    def __add_found_node(self, node):
        if not isinstance(node, RemoteNode):
            return False
        node.controller = self

        # Adds standard object attributes and properties
        for obj in node.objects:
            std_obj = self.get_standard_object((obj.group_code, obj.class_code))
            if isinstance(std_obj, Object):
                obj.name = std_obj.name
                for std_prop in std_obj.properties:
                    prop = std_prop.copy()
                    obj.add_property(prop)

        if node.ip not in self.__found_nodes:
            self.__notify_node_added(node)
        else:
            self.__notify_node_updated(node)

        self.__found_nodes[node.ip] = node

        return True

    def announce_message(self, msg: Message) -> bool:
        """Posts a multicast message to the same local network asynchronously.
        """
        return self.__node.announce_message(msg)

    def send_message(self, msg: Message, addr: Union[Tuple[str, int], str, RemoteNode]) -> bool:
        """Posts a unicast message to the specified node asynchronously.

            Args:
                msg (Message): The request message.
                addr (string): The node ip address.
        """
        to_addr = addr
        if isinstance(addr, RemoteNode):
            to_addr = (addr.ip, addr.port)
        elif isinstance(addr, str):
            to_addr = (addr, Node.PORT)
        return self.__node.send_message(msg, to_addr)

    def search(self) -> bool:
        """Posts a multicast read request to search all nodes in the same local network asynchronously.
        """
        msg = Controller.__SearchMessage()
        return self.announce_message(msg)

    def post_message(self, msg: Message, addr: Union[Tuple[str, int], str, RemoteNode]) -> Optional[Message]:
        """Posts a unicast message to the specified node and return the response message synchronously.

            Args:
                msg (Message): The request message.
                addr (string): The node ip address.

            Returns:
                Message: The response message for success, otherwise None.
        """
        self.__last_post_msg = Controller.__PostMessage()
        self.__last_post_msg.request = msg

        if not self.send_message(msg, addr):
            return None

        for i in range(DEFAULT_POST_MSG_RERTY):
            time.sleep(DEFAULT_POST_MSG_WAIT)
            if self.__last_post_msg.response is not None:
                break

        return self.__last_post_msg.response

    def start(self) -> Any:
        """Starts the controller to listen to any multicast and unicast messages from other nodes in the same local network, and executes search() after starting.
        """
        if not self.__node.start():
            return False
        self.__node.add_observer(self)
        self.search()
        return True

    def stop(self) -> Any:
        """ Stops the controller not to listen to any messages.
        """
        if not self.__node.stop():
            return False
        return True

    def _message_received(self, prpto_msg: ProtocolMessage):
        msg = Message(prpto_msg)

        if self.__is_node_profile_message(msg):
            node = RemoteNode()
            node.set_address(msg.from_addr)
            if node.parse_message(msg):
                self.__add_found_node(node)

        if self.__last_post_msg.is_waiting():
            if self.__last_post_msg.request.is_response(msg):
                self.__last_post_msg.response = msg
