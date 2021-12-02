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

from flask import url_for
from flask_restx import fields


class ObjectUrl(fields.Raw):
    __schema_type__ = "string"

    def __init__(self, object_class, object_id=None, **kwargs):
        super(ObjectUrl, self).__init__(**kwargs)
        self._object_class = object_class
        self._object_id = object_id

    def format(self, value):
        if self._object_id is not None:
            print(f"object_class: [{type(self._object_class)}] {self._object_class}")
            print(f"object_id: [{type(self._object_id)}] {self._object_id}")
            print(f"value: [{type(value)}] {value}")
            try:
                value = value[self._object_id]
            except (KeyError, IndexError, TypeError):
                value = getattr(value, self._object_id)

        return url_for(self._object_class, id=value)


class SubUrl(fields.Raw):
    __schema_type__ = "string"

    def __init__(self, object_class, subfield, **kwargs):
        super(SubUrl, self).__init__(**kwargs)
        self._object_class = object_class
        self._subfield = subfield

    def format(self, value):
        if isinstance(self._object_class, str):
            url = url_for(self._object_class, id=value)
        else:
            url = api.url_for(self._object_class, id=value)

        return '{}/{}'.format(url, self._subfield)
