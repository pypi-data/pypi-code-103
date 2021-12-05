# Copyright (C) 2021 Satoshi Konno. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License")
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

import copy
from typing import List
from .protocol.property import Property as ProtocolProperty


class Property(ProtocolProperty):
    """Property represents a property of ECHONET Lite, and it includes the specification attributes and the dynamic data.
    """

    CODE_MIN = 0x80
    CODE_MAX = 0xFF

    GET = 0
    SET = 1
    ANNO = 2
    ANNO_STATUS = 3

    PROHIBITED = 0
    REQUIRED = 1
    OPTIONAL = 2

    attrs: List[int]
    name: str
    size: int
    anno_status: bool

    def __init__(self):
        super().__init__()
        self.attrs = [Property.PROHIBITED, Property.PROHIBITED, Property.PROHIBITED, Property.PROHIBITED]

    def set_attribute(self, typ: int, attr: int):
        self.attrs[typ] = attr

    def get_attribute(self, typ: int) -> int:
        return self.attrs[typ]

    def __is_attribute_enabled(self, val) -> bool:
        if (val & Property.REQUIRED):
            return True
        if (val & Property.OPTIONAL):
            return True
        return False

    def __is_attribute_required(self, val) -> bool:
        if (val & Property.REQUIRED):
            return True
        return False

    def is_read_enabled(self) -> bool:
        return self.__is_attribute_enabled(self.attrs[Property.GET])

    def is_write_enabled(self) -> bool:
        return self.__is_attribute_enabled(self.attrs[Property.SET])

    def is_announce_enabled(self) -> bool:
        return self.__is_attribute_enabled(self.attrs[Property.ANNO])

    def is_read_required(self) -> bool:
        return self.__is_attribute_required(self.attrs[Property.GET])

    def is_write_required(self) -> bool:
        return self.__is_attribute_required(self.attrs[Property.SET])

    def is_announce_required(self) -> bool:
        return self.__is_attribute_required(self.attrs[Property.ANNO])

    def is_status_change_required(self) -> bool:
        return self.__is_attribute_enabled(self.attrs[Property.ANNO_STATUS])

    def copy(self):
        return copy.deepcopy(self)
