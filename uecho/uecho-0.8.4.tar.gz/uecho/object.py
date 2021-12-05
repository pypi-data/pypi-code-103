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

from typing import Optional, Union, Tuple, Dict, Any, List

from .property import Property


class Object(object):
    """Object represents a object of ECHONET Lite, and it has child properties that includes the specification attributes and the dynamic data.
    """

    CODE_MIN = 0x000000
    CODE_MAX = 0xFFFFFF
    CODE_SIZE = 3
    CODE_UNKNOWN = CODE_MIN

    OPERATING_STATUS = 0x80
    MANUFACTURER_CODE = 0x8A
    ANNO_PROPERTY_MAP = 0x9D
    SET_PROPERTY_MAP = 0x9E
    GET_PROPERTY_MAP = 0x9F

    OPERATING_STATUS_ON = 0x30
    OPERATING_STATUS_OFF = 0x31
    OPERATING_STATUS_SIZE = 1
    MANUFACTURER_EVALUATION_CODE_MIN = 0xFFFFF0
    MANUFACTURER_EVALUATION_CODE_MAX = 0xFFFFFF
    MANUFACTURER_CODE_SIZE = 3
    PROPERTY_MAP_MAX_SIZE = 16
    ANNO_PROPERTY_MAP_MAX_SIZE = PROPERTY_MAP_MAX_SIZE + 1
    SET_PROPERTY_MAP_MAX_SIZE = PROPERTY_MAP_MAX_SIZE + 1
    GET_PROPERTY_MAP_MAX_SIZE = PROPERTY_MAP_MAX_SIZE + 1

    MANUFACTURER_UNKNOWN = MANUFACTURER_EVALUATION_CODE_MIN

    code: int
    name: str
    __properties: Dict[int, Property]

    def __init__(self):
        self.code = 0
        self.name = ""
        self.__properties = {}
        pass

    def set_code(self, code: Union[int, Tuple[int, int], Tuple[int, int, int], Any]) -> bool:
        if isinstance(code, Object):
            self.code = code.code
        elif type(code) is int:
            self.code = code
            return True
        elif type(code) is tuple:
            tuple_n = len(code)
            if tuple_n == 2:
                self.code = 0
                self.group_code = code[0]
                self.class_code = code[1]
                return True
            elif tuple_n == 3:
                self.code = 0
                self.group_code = code[0]
                self.class_code = code[1]
                self.instance_code = code[2]
                return True
        return False

    @property
    def group_code(self):
        return ((self.code >> 16) & 0xFF)

    @group_code.setter
    def group_code(self, code: int):
        self.code |= ((code & 0xFF) << 16)

    @property
    def class_code(self):
        return ((self.code >> 8) & 0xFF)

    @class_code.setter
    def class_code(self, code: int):
        self.code |= ((code & 0xFF) << 8)

    @property
    def instance_code(self):
        return (self.code & 0xFF)

    @instance_code.setter
    def instance_code(self, code: int):
        self.code |= (code & 0xFF)

    @property
    def properties(self) -> List[Property]:
        return self.__properties.values()

    def add_property(self, prop: Property) -> bool:
        if not isinstance(prop, Property):
            return False
        self.__properties[prop.code] = prop
        return True

    def get_property(self, code: int) -> Optional[Property]:
        try:
            return self.__properties[code]
        except KeyError:
            return None

    def copy(self):
        obj = Object()
        obj.code = self.code
        obj.name = self.name
        for prop in self.__properties:
            obj.add_property(prop.copy())
        return obj
