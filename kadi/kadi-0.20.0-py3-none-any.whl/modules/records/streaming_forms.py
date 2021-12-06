# Copyright 2021 Karlsruhe Institute of Technology
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
from streaming_form_data.targets import BaseTarget
from streaming_form_data.targets import ValueTarget

from kadi.lib.api.core import json_error_response
from kadi.lib.exceptions import KadiFilesizeExceededError
from kadi.lib.format import filesize


class KadiValueTarget(ValueTarget):
    r"""Extended `ValueTarget` for use in streaming form data parsers.

    :param \*args: Additional arguments to pass to the `ValueTarget`.
    :param on_finish: (optional) A callback that will be invoked with the parsed value
        once the parser is done processing the respective input.
    :param \**kwargs: Additional keyword arguments to pass to the `ValueTarget`.
    """

    def __init__(self, *args, on_finish=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._on_finish = on_finish

    def on_finish(self):
        if self._on_finish is not None:
            self._on_finish(self.value)


class StorageTarget(BaseTarget):
    r"""Extended `BaseTarget` for use in streaming form data parsers.

    For use in file uploads to directly store received file data in a storage.

    :param file_factory: A factory function that needs to return a tuple containing a
        storage, an open file handle and the maximum allowed size of the file.
    :param \*args: Additional arguments to pass to the `BaseTarget`.
    :param on_data_received: (optional) A callback that will be invoked with each
        received chunk of the uploaded file.
    :param on_upload_finished: (optional) A callback that will be invoked with the final
        size of the uploaded file.
    :param on_error: (optional) A callback that will be invoked with an error response
        if an error during the upload occured.
    :param \**kwargs: Additional keyword arguments to pass to the `BaseTarget`.
    """

    def __init__(
        self,
        file_factory,
        *args,
        on_data_received=None,
        on_upload_finished=None,
        on_error=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.file_factory = file_factory
        self.size_uploaded = 0
        self._response = None
        self._on_data_received = on_data_received
        self._on_upload_finished = on_upload_finished
        self._on_error = on_error

    def on_start(self):
        self.storage, self.file, self.max_size = self.file_factory()

    def on_data_received(self, chunk):
        self.size_uploaded += len(chunk)

        # Check if the file size exceeds the size provided in the form.
        if self.size_uploaded > self.max_size:
            description = f"Maximum upload size exceeded ({filesize(self.max_size)})."

            # Store the response as the parser catches the raised exception. The
            # response is passed later to the caller.
            self._response = json_error_response(413, description=description)

            raise KadiFilesizeExceededError

        self.file.write(chunk)

        if self._on_data_received is not None:
            self._on_data_received(chunk)

    def on_finish(self):
        self.storage.close(self.file)

        # Error occured.
        if self._response is not None and self._on_error is not None:
            self._on_error(self._response)
            return

        if self._on_upload_finished is not None:
            self._on_upload_finished(self.size_uploaded)


def value_to_string(value):
    """Converts a value from a `ValueTarget` to string.

    :param value: The value.
    :return: The value as string.
    """
    return value.decode()


def value_to_int(value):
    """Converts a value from a `ValueTarget` to int.

    :param value: The value.
    :return: The value as int.
    """
    return int(value_to_string(value))
