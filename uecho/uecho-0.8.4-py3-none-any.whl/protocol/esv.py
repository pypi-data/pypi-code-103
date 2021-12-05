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


class ESV(object):
    """
    ESV represents a ESV code in a protocol message of Echonet Lite.
    """
    UNKNOWN = 0x00
    WRITE_REQUEST = 0x60
    WRITE_REQUEST_RESPONSE_REQUIRED = 0x61
    READ_REQUEST = 0x62
    NOTIFICATION_REQUEST = 0x63
    WRITE_READ_REQUEST = 0x6E
    WRITE_RESPONSE = 0x71
    READ_RESPONSE = 0x72
    NOTIFICATION = 0x73
    NOTIFICATION_RESPONSE_REQUIRED = 0x74
    NOTIFICATION_RESPONSE = 0x7A
    WRITE_READ_RESPONSE = 0x7E
    WRITE_REQUEST_ERROR = 0x50
    WRITE_REQUEST_RESPONSE_REQUIRED_ERROR = 0x51
    READ_REQUEST_ERROR = 0x52
    NOTIFICATION_REQUEST_ERROR = 0x53
    WRITE_READ_REQUEST_ERROR = 0x5E

    def __init__(self, code=UNKNOWN):
        self.ESV = code
