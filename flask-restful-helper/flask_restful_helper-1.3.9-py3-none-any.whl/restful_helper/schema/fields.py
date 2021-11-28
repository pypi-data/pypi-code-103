import json

from marshmallow import fields


class JsonField(fields.Field):
    """Field that serializes to a string of numbers and deserializes
    to a list of numbers.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return {}
        return json.loads(value)

    def _deserialize(self, value, attr, data, **kwargs):
        return json.dumps(value)
