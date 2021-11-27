# Copyright 2021 Torsten Mehnert
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import json
from .todo import TodoWithSlots, TodoWithProps
from .timespan import Timespan


class Encoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, TodoWithSlots) or isinstance(o, TodoWithProps):
            return {
                "updateLink": o.updateLink,
                "description": o.description,
                "what": o.what,
                "timespan": o.timespan
            }

        if isinstance(o, Timespan):
            return {
                "amount": o.amount,
                "unit": o.unit,
                "veryLate": o.veryLate
            }

        return json.JSONEncoder.default(self, o)
