from rest_framework import serializers

from django_pay2.models import Payment
from django_pay2.utils import MappingFieldsMixin

from .services import get_tinkoff_api


class RawDataDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context["request"].data

    def __repr__(self):
        return "%s()" % self.__class__.__name__


class NotifySerializer(MappingFieldsMixin, serializers.Serializer):
    terminal_key = serializers.CharField()
    token = serializers.CharField()
    payment = serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all())
    is_success = serializers.BooleanField()
    amount_rub = serializers.IntegerField()
    raw_data = serializers.HiddenField(default=RawDataDefault())

    mapping_keys = {
        "terminal_key": "TerminalKey",
        "token": "Token",
        "payment": "OrderId",
        "is_success": "Success",
        "amount_rub": "Amount",
    }

    default_error_messages = {
        "unexpected_terminal_token": "Unexpected terminal token",
        "must_be_success": "Payment must be success",
        "mismatch_token": "Mismatch token",
        "mismatch_amount": "Mismatch amount",
    }

    def validate_terminal_key(self, key):
        if get_tinkoff_api().terminal_key != key:
            self.fail("unexpected_terminal_key")
        return key

    def validate_is_success(self, is_success):
        if not is_success:
            self.fail("must_be_success")
        return is_success

    def validate_amount_rub(self, amount):
        return amount * 100

    def validate(self, attrs):
        attrs = super().validate(attrs)

        expected_token = get_tinkoff_api().calculate_token(attrs["raw_data"])
        if attrs["token"] != expected_token:
            self.fail("mismatch_token")

        if attrs["payment"].amount != attrs["amount_rub"]:
            self.fail("mismatch_amount")

        return attrs
