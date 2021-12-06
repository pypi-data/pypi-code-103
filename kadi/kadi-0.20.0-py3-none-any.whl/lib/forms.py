# Copyright 2020 Karlsruhe Institute of Technology
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
from datetime import timezone

from flask_babel import gettext as _
from flask_babel import ngettext
from flask_wtf import FlaskForm
from wtforms import BooleanField as _BooleanField
from wtforms import DateTimeField
from wtforms import FileField as _FileField
from wtforms import IntegerField as _IntegerField
from wtforms import PasswordField as _PasswordField
from wtforms import SelectField as _SelectField
from wtforms import SelectMultipleField
from wtforms import StringField as _StringField
from wtforms import SubmitField as _SubmitField
from wtforms import TextAreaField
from wtforms.validators import Length
from wtforms.validators import StopValidation

from .conversion import lower
from .conversion import normalize
from .validation import validate_identifier as _validate_identifier
from .validation import validate_mimetype as _validate_mimetype
from .validation import validate_username as _validate_username
from .validation import validate_uuid
from .validation import validator
from kadi.lib.utils import compact_json


class KadiForm(FlaskForm):
    """Base class for all forms.

    :param _suffix: (optional) A suffix that will be appended to all field IDs in the
        form of ``"<id>_<suffix>"``. This is especially useful when dealing with
        multiple forms on the same page.
    """

    def __init__(self, *args, _suffix=None, **kwargs):
        super().__init__(*args, **kwargs)

        if _suffix is not None:
            for field in self._fields.values():
                field.id = f"{field.id}_{_suffix}"
                field.label.field_id = field.id


class DictFieldMixin:
    """Mixin class to add a common dictionary conversion method to custom fields."""

    def to_dict(self):
        """Convert this field into a dictionary representation."""
        data = {
            "id": self.id,
            "name": self.name,
            "label": str(self.label.text),
            "description": str(self.description),
            "errors": self.errors or [],
            "data": self.data,
        }

        if self.data is None:
            data["data"] = ""

        validation = {
            "required": self.flags.required,
        }

        for validator in self.validators:
            if isinstance(validator, Length):
                if validator.min != -1:
                    validation["min"] = validator.min

                if validator.max != -1:
                    validation["max"] = validator.max

        data["validation"] = validation
        return data


class BooleanField(_BooleanField, DictFieldMixin):
    """Regular boolean field inheriting from :class:`DictFieldMixin`."""


class IntegerField(_IntegerField, DictFieldMixin):
    """Regular integer field inheriting from :class:`DictFieldMixin`."""


class PasswordField(_PasswordField, DictFieldMixin):
    """Regular password field inheriting from :class:`DictFieldMixin`."""


class StringField(_StringField, DictFieldMixin):
    """Regular string field inheriting from :class:`DictFieldMixin`."""


class SubmitField(_SubmitField, DictFieldMixin):
    """Regular submit field inheriting from :class:`DictFieldMixin`."""


class FileField(_FileField, DictFieldMixin):
    """Custom file field."""

    def to_dict(self):
        data = super().to_dict()
        data["data"] = None

        return data


class LFTextAreaField(TextAreaField, DictFieldMixin):
    """Custom text area field that converts *CRLF* to *LF*."""

    def process_formdata(self, valuelist):
        r"""Convert each occurence of \\r\\n to \\n."""
        super().process_formdata(valuelist)

        if self.data is not None:
            self.data = self.data.replace("\r\n", "\n")


class UTCDateTimeField(DateTimeField, DictFieldMixin):
    """Custom timezone aware DateTimeField using UTC.

    :param date_format: (optional) The date format to use for parsing and serializing.
    """

    def __init__(self, *args, date_format="%Y-%m-%dT%H:%M:%S.%fZ", **kwargs):
        kwargs["format"] = date_format
        super().__init__(*args, **kwargs)

    def process_formdata(self, valuelist):
        """Replace the missing timezone with UTC."""
        super().process_formdata(valuelist)

        if self.data is not None:
            self.data = self.data.replace(tzinfo=timezone.utc)

    def to_dict(self):
        data = super().to_dict()
        data["data"] = self._value()

        return data


class SelectField(_SelectField, DictFieldMixin):
    """Regular select field inheriting from :class:`DictFieldMixin`."""

    def to_dict(self):
        data = super().to_dict()

        if self.choices is not None:
            data["choices"] = [(val, str(title)) for val, title in self.choices]
        else:
            data["choices"] = []

        return data


class DynamicSelectField(_SelectField, DictFieldMixin):
    """Custom select field for dynamically generated selections.

    The instance variable ``initial`` can be used to set an initial value to prefill the
    selection with.
    """

    def __init__(self, *args, **kwargs):
        self.initial = None

        kwargs["default"] = None
        kwargs["choices"] = []
        kwargs["validate_choice"] = False

        super().__init__(*args, **kwargs)

    def to_dict(self):
        data = super().to_dict()
        data["data"] = self.initial

        return data


class DynamicMultiSelectField(SelectMultipleField, DictFieldMixin):
    """Custom multi select field for dynamically generated selections.

    The instance variable ``initial`` can be used to set initial values to prefill the
    selection with.
    """

    def __init__(self, *args, **kwargs):
        self.initial = []

        kwargs["default"] = []
        kwargs["choices"] = []
        kwargs["validate_choice"] = False

        super().__init__(*args, **kwargs)

    def to_dict(self):
        data = super().to_dict()
        data["data"] = self.initial

        return data


class TagsField(DynamicMultiSelectField):
    """Custom dynamic multi select field specifically for tags.

    :param max_len: (optional) The maximum length of each tag.
    """

    def __init__(self, *args, max_len=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_len = max_len

    def post_validate(self, form, validation_stopped):
        """Validate each tag.

        Does not allow empty tags and optionally checks their maximum length as well.
        """
        for value in self.data:
            if not value:
                self.errors = [_("Tags must not be empty.")]
                return False

            if self.max_len is not None and len(value) > self.max_len:
                self.errors = [
                    ngettext(
                        "Tags cannot be longer than %(num)d character.",
                        "Tags cannot be longer than %(num)d characters.",
                        num=self.max_len,
                    )
                ]
                return False

        return True

    def process_formdata(self, valuelist):
        """Convert each tag to lowercase and remove/normalize whitespace."""
        super().process_formdata(valuelist)

        data = []
        for value in self.data:
            for converter in [lower, normalize]:
                value = converter(value)

            if value not in data:
                data.append(value)

        self.data = data


class ValidateUUID:
    """Validate a UUID of a specific version in a form field.

    :param version: (optional) The UUID version.
    """

    def __init__(self, version=4):
        self.version = version

    @validator(StopValidation)
    def __call__(self, form, field):
        validate_uuid(field.data, version=self.version)


@validator(StopValidation)
def validate_identifier(form, field):
    """Validate an identifier in a form field.

    Uses :func:`kadi.lib.validation.validate_identifier`.

    :param form: The form object.
    :param field: The field object.
    """
    _validate_identifier(field.data)


@validator(StopValidation)
def validate_mimetype(form, field):
    """Validate a MIME type in a form field.

    Uses :func:`kadi.lib.validation.validate_mimetype`.

    :param form: The form object.
    :param field: The field object.
    """
    _validate_mimetype(field.data)


@validator(StopValidation)
def validate_username(form, field):
    """Validate a local username in a form field.

    Uses :func:`kadi.lib.validation.validate_username`.

    :param form: The form object.
    :param field: The field object.
    """
    _validate_username(field.data)


def check_duplicate_identifier(field, model, exclude=None):
    """Check for a duplicate identifier in a form field.

    Has to be called manually after the usual validation as further arguments are needed
    for this check.

    :param field: The identifier field.
    :param model: The model the check the identifier in.
    :param exclude: (optional) An object that should be excluded in the check.
    """
    identifier = field.data
    if identifier is not None:
        obj_to_check = model.query.filter_by(identifier=identifier).first()

        if obj_to_check is not None and (exclude is None or exclude != obj_to_check):
            raise StopValidation(_("Identifier is already in use."))


def json_field(field):
    """Convert a form field into a JSON representation.

    :param field: The form field to convert.
    :return: The converted form field.
    """
    return compact_json(field.to_dict())
