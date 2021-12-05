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

from typing import Optional, Union, Tuple

from .manufacture import Manufacture
from .object import Object
from .objects import get_all_std_objects
from .manufacturers import get_all_std_manufactures
from ..util import Bytes


class Database():

    __manufacturers: dict
    __objects: dict

    def __init__(self):
        self.__manufacturers = get_all_std_manufactures()
        self.__objects = get_all_std_objects()

    def __get_manufacturer(self, code: int) -> Optional[Manufacture]:
        try:
            return self.__manufacturers[(code)]
        except KeyError:
            return None

    def get_manufacturer(self, code: Union[int, bytes]) -> Optional[Manufacture]:
        man_code = 0
        if isinstance(code, int):
            man_code = code
        elif isinstance(code, bytes):
            man_code = Bytes.to_int(code)
        return self.__get_manufacturer(man_code)

    def get_manufacturer_name(self, code: Union[int, bytes]) -> Optional[str]:
        man = self.get_manufacturer(code)
        if man is not None:
            return man.name
        return None

    def __get_object(self, grp_code: int, cls_code: int) -> Optional[Object]:
        try:
            return self.__objects[(grp_code, cls_code)]
        except KeyError:
            return None

    def get_object(self, code: Union[Object, int, Tuple[int, int]]) -> Optional[Object]:
        obj = Object()
        if not obj.set_code(code):
            return None
        return self.__get_object(obj.group_code, obj.class_code)
