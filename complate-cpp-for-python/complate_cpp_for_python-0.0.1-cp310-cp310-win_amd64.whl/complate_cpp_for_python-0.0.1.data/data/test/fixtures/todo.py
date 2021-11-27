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


class TodoWithSlots:
    __slots__ = ["what", "description", "updateLink", "timespan"]

    def __init__(self, what, description, updateLink, timespan):
        self.what = what
        self.description = description
        self.updateLink = updateLink
        self.timespan = timespan


class TodoWithProps:
    def __init__(self, what, description, updateLink, timespan):
        self._what = what
        self._description = description
        self._updateLink = updateLink
        self._timespan = timespan

    @property
    def what(self): return self._what

    @property
    def description(self): return self._description

    @property
    def updateLink(self): return self._updateLink

    @property
    def timespan(self): return self._timespan
