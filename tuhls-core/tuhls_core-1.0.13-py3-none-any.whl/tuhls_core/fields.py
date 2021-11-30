from datetime import datetime

from rest_framework import serializers
from rest_framework.fields import ListField


class StringArrayField(ListField):
    def to_representation(self, obj):
        return ",".join(str(element) for element in obj.all())

    def to_internal_value(self, data):
        return super().to_internal_value(data.split(","))


class NestedSerializerWriteableRelationMixin:
    def __init__(self, **kwargs):
        self.serializer = kwargs.pop("serializer", None)
        if self.serializer is not None and not issubclass(
            self.serializer, serializers.Serializer
        ):
            raise TypeError('"serializer" is not a valid serializer class')
        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        return False if self.serializer else True

    def to_representation(self, instance):
        if self.serializer:
            return self.serializer(instance, context=self.context).data
        return super().to_representation(instance)


class TimestampField(serializers.DateTimeField):
    """
    Convert a django datetime to/from timestamp.
    """

    def to_representation(self, value):
        """
        Convert the field to its internal representation (aka timestamp)
        :param value: the DateTime value
        :return: a UTC timestamp integer
        """
        return value.timestamp()

    def to_internal_value(self, value):
        """
        deserialize a timestamp to a DateTime value
        :param value: the timestamp value
        :return: a django DateTime value
        """
        return datetime.fromtimestamp(float(value))
