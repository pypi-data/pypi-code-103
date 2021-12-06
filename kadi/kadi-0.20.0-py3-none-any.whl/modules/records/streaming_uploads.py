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
import hashlib
import json

from flask import abort
from flask_login import current_user
from streaming_form_data.parser import StreamingFormDataParser

from .streaming_forms import KadiValueTarget
from .streaming_forms import StorageTarget
from .streaming_forms import value_to_int
from .streaming_forms import value_to_string
from kadi.ext.db import db
from kadi.lib.api.core import json_error_response
from kadi.lib.db import update_object
from kadi.lib.storage.core import get_storage
from kadi.lib.storage.core import get_storages
from kadi.modules.records.api.utils import check_file_exists
from kadi.modules.records.api.utils import check_max_upload_size
from kadi.modules.records.api.utils import check_upload_user_quota
from kadi.modules.records.models import File
from kadi.modules.records.models import Upload
from kadi.modules.records.schemas import UploadSchema
from kadi.modules.records.uploads import complete_file_upload


class StreamingForm:
    """Holds all values submitted by the form.

    Is filled continuously as the form is parsed value by value.
    """

    def __init__(self):
        self.storage_type = None
        self.replace_file = False
        self.name = None
        self.size = 0
        self.mimetype = "application/octet-stream"
        self.checksum = None


class StreamingContext:
    """Container class used to pass information between the single parsing stages."""

    def __init__(self):
        self.form = StreamingForm()
        self.storage = None
        self.upload_started = False
        self.replaced_file = None
        self.record = None
        self.upload = None
        self.file = None
        self.file_exists = False
        self.calculated_checksum = hashlib.md5()


def abort_if_not_none(response):
    """Checks if the response is ``None``, if not the request is aborted.

    :param response: The potential response.
    """
    if response is not None:
        abort(response)


def validate_storage_type(streaming_context):
    """Checks if the used storage type is registered.

    :param streaming_context: The :class:`.StreamingContext`.
    """

    def _validate_storage_type(value):
        storage_type = value_to_string(value)
        streaming_context.form.storage_type = storage_type

        response = (
            None
            if storage_type in get_storages()
            else json_error_response(
                400, description=f"Selected storage '{storage_type}' is not registered."
            )
        )

        abort_if_not_none(response)

    return _validate_storage_type


def validate_filename(streaming_context):
    """Checks if the file name is valid.

    :param streaming_context: The :class:`.StreamingContext`.
    """

    def _validate_filename(value):
        name = value_to_string(value)
        name = UploadSchema(only=["name"]).load_or_400({"name": name})["name"]

        streaming_context.form.name = name

        response = check_file_exists(streaming_context.record, name)

        if response is not None:
            streaming_context.file_exists = True

            if not streaming_context.form.replace_file:
                abort_if_not_none(response)
            else:
                # Store the replaced file so in the case of a force replace we can show
                # that a file is replaced.
                streaming_context.replaced_file = json.loads(response.data)["file"]

    return _validate_filename


def validate_filesize(streaming_context):
    """Checks if any limits for the file size are exceeded.

    :param streaming_context: The :class:`.StreamingContext`.
    """

    def _validate_filesize(value):
        size = value_to_int(value)
        size = UploadSchema(only=["size"]).load_or_400({"size": size})["size"]

        streaming_context.form.size = size
        additional_size = size

        if streaming_context.replaced_file is not None:
            additional_size -= streaming_context.replaced_file["size"]

        abort_if_not_none(check_max_upload_size(size))
        abort_if_not_none(check_upload_user_quota(additional_size=additional_size))

    return _validate_filesize


def validate_mimetype(streaming_context):
    """Checks if the mimetype is valid.

    :param streaming_context: The :class:`.StreamingContext`.
    """

    def _validate_mimetype(value):
        streaming_context.form.mimetype = UploadSchema(only=["mimetype"]).load_or_400(
            {"mimetype": value_to_string(value)}
        )["mimetype"]

    return _validate_mimetype


def validate_checksum(streaming_context):
    """Checks if the checksum is valid.

    :param streaming_context: The :class:`.StreamingContext`.
    """

    def _validate_checksum(value):
        streaming_context.form.checksum = UploadSchema(only=["checksum"]).load_or_400(
            {"checksum": value_to_string(value)}
        )["checksum"]

    return _validate_checksum


def file_factory(streaming_context):
    """Factory to create a storage and corresponding file.

    :param streaming_context: The :class:`.StreamingContext`.
    """

    def _file_factory():
        storage_type = streaming_context.form.storage_type
        file_name = streaming_context.form.name
        file_size = streaming_context.form.size

        storage = get_storage(storage_type)
        streaming_context.storage = storage

        upload = Upload.create(
            creator=current_user,
            record=streaming_context.record,
            name=file_name,
            size=file_size,
            storage_type=storage.storage_type,
            upload_type=storage.upload_type,
            mimetype=streaming_context.form.mimetype,
            checksum=streaming_context.form.checksum,
        )

        # Associate the upload with the existing file, if there is one.
        if streaming_context.replaced_file:
            upload.file = streaming_context.record.active_files.filter(
                File.name == file_name
            ).first()

        db.session.commit()

        streaming_context.upload = upload

        filepath = storage.create_filepath(str(streaming_context.upload.id))
        storage.ensure_filepath_exists(filepath)

        streaming_context.upload_started = True

        return (storage, storage.open(filepath, "wb"), file_size)

    return _file_factory


def finish_upload(streaming_context):
    """Updates the remaining information of the file after the upload finished.

    Uses :func:`complete_file_upload` to complete the file upload process.

    :param streaming_context: The :class:`.StreamingContext`.
    """

    def _finish_upload(size_uploaded):
        streaming_context.form.size = size_uploaded

        upload = streaming_context.upload
        checksum = upload.checksum or streaming_context.calculated_checksum.hexdigest()

        update_object(
            upload,
            size=size_uploaded,
            calculated_checksum=streaming_context.calculated_checksum.hexdigest(),
            checksum=checksum,
        )

        streaming_context.upload_started = False

        streaming_context.file = complete_file_upload(
            streaming_context.storage, streaming_context.upload
        )

    return _finish_upload


def create_streaming_parser(headers, streaming_context):
    """Creates a `StreamingFormDataParser` suitable to handle direct file uploads.

    Note that during the file streaming one or more database commits are issued.

    :param headers: The HTTP-headers of the request the parser is used in.
    :param streaming_context: The :class:`.StreamingContext`.
    """

    def on_replace_file_received(value):
        streaming_context.form.replace_file = value_to_string(value).lower() == "true"

    def on_data_received(chunk):
        streaming_context.calculated_checksum.update(chunk)

    def on_error(response):
        abort_if_not_none(response)

    parser = StreamingFormDataParser(headers=headers)

    parser.register(
        "storage_type",
        KadiValueTarget(on_finish=validate_storage_type(streaming_context)),
    )
    parser.register(
        "replace_file",
        KadiValueTarget(on_finish=on_replace_file_received),
    )
    parser.register(
        "name",
        KadiValueTarget(on_finish=validate_filename(streaming_context)),
    )
    parser.register(
        "size",
        KadiValueTarget(on_finish=validate_filesize(streaming_context)),
    )
    parser.register(
        "mimetype", KadiValueTarget(on_finish=validate_mimetype(streaming_context))
    )
    parser.register(
        "checksum", KadiValueTarget(on_finish=validate_checksum(streaming_context))
    )
    parser.register(
        "blob",
        StorageTarget(
            file_factory(streaming_context),
            on_data_received=on_data_received,
            on_upload_finished=finish_upload(streaming_context),
            on_error=on_error,
        ),
    )

    return parser
