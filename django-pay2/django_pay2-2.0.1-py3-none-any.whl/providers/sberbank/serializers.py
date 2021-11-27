import hashlib
import hmac

from rest_framework import serializers

from django_pay2.models import Payment
from django_pay2.settings import payment_settings
from django_pay2.utils import MappingFieldsMixin

from .constants import SberbankCallbackOperation, SberbankCallbackStatus


class SberbankCallbackSerializer(MappingFieldsMixin, serializers.Serializer):
    # TODO: посмотреть на amount и почему он integer
    amount = serializers.IntegerField()
    md_order = serializers.CharField()
    order_num = serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all())
    checksum = serializers.CharField()
    operation = serializers.ChoiceField(SberbankCallbackOperation.choices)
    status = serializers.ChoiceField(SberbankCallbackStatus.choices)

    default_error_messages = {
        "invalid_checksum": 'Expected "{expected}", given "{given}"',
        "mismatch_amount": "Expected {expected}, given {given}",
    }

    mapping_keys = {
        "md_order": "mdOrder",
        "order_num": "orderNumber",
    }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        payment = attrs["order_num"]
        if attrs["amount"] != payment.amount:
            self.fail("mismatch_amount", expected=payment.amount, given=attrs["amount"])
        return attrs

    def validate_checksum(self, given):
        checksum_data = self.initial_data.copy()
        checksum_data.pop("checksum")
        checksum_data.pop("sign_alias", None)
        checksum_str = (
            ";".join(
                f"{key};{checksum_data[key]}" for key in sorted(checksum_data.keys())
            )
            + ";"
        )
        expected = (
            hmac.new(
                payment_settings.SBERBANK.public_key.encode("utf-8"),
                checksum_str.encode("utf-8"),
                hashlib.sha256,
            )
            .hexdigest()
            .upper()
        )
        if given != expected:
            self.fail("invalid_checksum", expected=expected, given=given)
        return given
