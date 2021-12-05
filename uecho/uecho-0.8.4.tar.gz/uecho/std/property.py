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

from typing import Any

from ..property import Property as PropertyBase


class Property(PropertyBase):
    typ: str

    def __init__(self, code: int, name: str, typ: str, size: int, get: Any, set: Any, anno: Any, chg: Any):
        super().__init__()
        self.code = code
        self.name = name
        self.typ = typ
        self.size = size
        self.set_attribute(PropertyBase.GET, self.__to_attribute(get))
        self.set_attribute(PropertyBase.SET, self.__to_attribute(set))
        self.set_attribute(PropertyBase.ANNO, self.__to_attribute(anno))
        self.set_attribute(PropertyBase.ANNO_STATUS, self.__to_attribute(chg))

    def __to_attribute(self, val: Any) -> int:
        attr = Property.PROHIBITED
        if isinstance(val, int):
            attr = val
        if isinstance(val, str):
            if val.lower() == "mandatory":
                attr = Property.REQUIRED
            elif val.lower() == "optional":
                attr = Property.OPTIONAL
        return attr
