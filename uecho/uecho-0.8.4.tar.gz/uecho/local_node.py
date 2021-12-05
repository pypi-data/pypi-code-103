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

from .transport.manager import Manager
from .node_profile import NodeProfile
from .protocol.message import Message


class LocalNode(Manager):

    def __init__(self):
        super().__init__()

    def announce_message(self, msg: Message) -> bool:
        msg.SEOJ = NodeProfile.CODE
        return super().announce_message(msg)

    def send_message(self, msg: Message, addr) -> bool:
        msg.SEOJ = NodeProfile.CODE
        return super().send_message(msg, addr)
