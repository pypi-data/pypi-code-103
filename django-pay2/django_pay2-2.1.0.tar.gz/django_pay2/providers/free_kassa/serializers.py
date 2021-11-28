from rest_framework import serializers

from django_pay2.models import Payment
from django_pay2.settings import payment_settings

from .api import get_api


class FreeKassaNotifySerializer(serializers.Serializer):
    merchant_id = serializers.CharField()
    amount = serializers.FloatField()
    order = serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all())
    sign = serializers.CharField()

    default_error_messages = {
        "incorrect_merchant_id": "Incorrect merchant ID",
        "amounts_not_equal": "Amounts are not equal",
        "incorrect_sign": "Incorrect sign",
    }

    def validate_merchant_id(self, value):
        if payment_settings.FREE_KASSA.merchant_id != value:
            self.fail("incorrect_merchant_id")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs["order"].amount != attrs["amount"]:
            self.fail("amounts_not_equal")
        api = get_api()
        expected_sign = api.generate_notify_sign(attrs["amount"], attrs["order"].id)
        if expected_sign != attrs["sign"]:
            self.fail("incorrect_sign")
        return attrs
