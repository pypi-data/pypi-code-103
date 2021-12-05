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

from .util import Bytes
from .node import Node
from .object import Object
from .node_profile import NodeProfile
from .message import Message


class RemoteNode(Node):

    def __init__(self):
        super().__init__()
        self.controller = None

    def parse_message(self, msg: Message) -> bool:
        if not isinstance(msg, Message):
            return False

        if msg.OPC < 1:
            return False

        prop = msg.properties[0]

        if prop.code != NodeProfile.CLASS_INSTANCE_LIST_NOTIFICATION and prop.code != NodeProfile.CLASS_SELF_NODE_INSTANCE_LIST_S:
            return False

        instance_count = prop.data[0]
        if len(prop.data) < ((instance_count * Object.CODE_SIZE) + 1):
            return False

        for n in range(instance_count):
            offset = (Object.CODE_SIZE * n) + 1
            code_bytes = prop.data[offset:(offset + Object.CODE_SIZE)]
            obj = Object()
            obj.set_code(Bytes.to_int(code_bytes))
            self.add_object(obj)

        return True
