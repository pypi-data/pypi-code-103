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
from complatecpp import Stream


class TestStream(Stream):
    __test__ = False

    def __init__(self, *args, **kwargs):
        # Don't use super()
        Stream.__init__(self, *args, **kwargs)
        self.data = str()

    def write(self, string, length):
        self.data += string[0:length]

    def writeln(self, string, length):
        self.data += string[0:length]
        self.data += '\n'

    def flush(self):
        pass

    def str(self):
        return self.data
