# Copyright 2017 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from werkzeug.exceptions import HTTPException


class TaskManagerError(Exception):
    pass


class TaskManagerHTTPError(TaskManagerError, HTTPException):
    """
    All exceptions that should lead to an HTTP error response
    """
    code = 500

    def __init__(self, description, response=None):
        super().__init__(description)
        self._description = description

    def __str__(self):
        return str(self._description)

    @property
    def description(self):
        return str(self)


class CouldNotFindResourceError(TaskManagerHTTPError):
    """
    Could not find a resource
    """
    code = 404

    def __init__(self, id_, type_, message=None):
        super().__init__(message)
        self.id = id_
        self.type =type_
        self.msg = message

    def __str__(self):
        if self.msg is not None:
            return self.msg.format(id=self.id, type_=self.type)
        else:
            return f"Could not find {self.type.__name__} with identifier {self.id!r}"


class InvalidArgumentsError(TaskManagerHTTPError):
    """
    Invalid (combination of) arguments
    """
    code = 400
