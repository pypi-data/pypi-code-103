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

from .object import Object


class NodeProfile(Object):
    CODE = 0x0EF001
    CLASS_CODE = 0xF0
    INSTANCE_GENERAL_CODE = 0x01
    INSTANCE_TRANSMISSION_ONLY_CODE = 0x02

    CLASS_OPERATING_STATUS = Object.OPERATING_STATUS
    CLASS_VERSION_INFORMATION = 0x82
    CLASS_IDENTIFICATION_NUMBER = 0x83
    CLASS_FAULT_CONTENT = 0x89
    CLASS_UNIQUE_IDENTIFIER_DATA = 0xBF
    CLASS_NUMBER_OF_SELF_NODE_INSTANCES = 0xD3
    CLASS_NUMBER_OF_SELF_NODE_CLASSES = 0xD4
    CLASS_INSTANCE_LIST_NOTIFICATION = 0xD5
    CLASS_SELF_NODE_INSTANCE_LIST_S = 0xD6
    CLASS_SELF_NODE_CLASS_LIST_S = 0xD7

    CLASS_OPERATING_STATUS_SIZE = 1
    CLASS_VERSION_INFORMATION_SIZE = 4
    CLASS_IDENTIFICATION_MANUFACTURER_CODE_SIZE = 3
    CLASS_IDENTIFICATION_UNIQUE_ID_SIZE = 13
    CLASS_IDENTIFICATION_NUMBER_SIZE = 1 + CLASS_IDENTIFICATION_MANUFACTURER_CODE_SIZE + CLASS_IDENTIFICATION_UNIQUE_ID_SIZE
    CLASS_FAULT_CONTENT_SIZE = 2
    CLASS_UNIQUE_IDENTIFIER_DATA_SIZE = 2
    CLASS_NUMBER_OF_SELF_NODE_INSTANCES_SIZE = 3
    CLASS_NUMBER_OF_SELF_NODE_CLASSES_SIZE = 2
    CLASS_SELF_NODE_INSTANCE_LIST_S_MAX = 0xFF
    CLASS_SELF_NODE_CLASS_LIST_S_MAX = 0xFF
    CLASS_INSTANCE_LIST_NOTIFICATION_MAX = CLASS_SELF_NODE_INSTANCE_LIST_S_MAX

    CLASS_OPERATING_STATUS_ON = Object.OPERATING_STATUS_ON
    CLASS_OPERATING_STATUS_OFF = Object.OPERATING_STATUS_OFF
    CLASS_BOOTING = 0x30
    CLASS_NOT_BOOTING = 0x31
    LOWER_COMMUNICATION_LAYER_PROTOCOL_TYPE = 0xFE

    def __init__(self):
        self.code = NodeProfile.CODE
        pass


class NodeProfileReadOnly(Object):
    CODE = 0x0EF002

    def __init__(self):
        super().__init__()
        self.code = NodeProfileReadOnly.CODE
