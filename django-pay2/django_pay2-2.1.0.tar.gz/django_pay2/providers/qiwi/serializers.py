from rest_framework import serializers

from django_pay2.models import Payment
from django_pay2.utils import HmacDefault

from .api import get_api


class StatusSerializer(serializers.Serializer):
    value = serializers.CharField()

    default_error_messages = {"unexpected_status": "Unexpected status"}

    def validate_value(self, value):
        if value != "PAID":
            self.fail("unexpected_status")
        return value


class AmountSerializer(serializers.Serializer):
    value = serializers.DecimalField(max_digits=20, decimal_places=2)
    currency = serializers.CharField()


class BillSerializer(serializers.Serializer):
    site_id = serializers.CharField()
    bill_id = serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all())
    amount = AmountSerializer()
    status = StatusSerializer()

    default_error_messages = {"mismatched_amount": "Mismatched amount"}

    def validate(self, attrs):
        attrs = super().validate(attrs)
        bill = attrs["bill_id"]
        if bill.amount != attrs["amount"]["value"]:
            self.fail("mismatched_amount")
        return attrs

    def to_internal_value(self, data):
        data = {
            "bill_id": data.get("billId"),
            "amount": data.get("amount"),
            "status": data.get("status"),
            "site_id": data.get("siteId"),
        }
        return super().to_internal_value(data)


class QiwiNotifySerializer(serializers.Serializer):
    bill = BillSerializer()
    hmac = serializers.HiddenField(default=HmacDefault())

    default_error_messages = {"mismatch_hmac": "Mismatch HMAC"}

    def validate(self, attrs):
        attrs = super().validate(attrs)
        expected_hmac = get_api().create_hmac(
            attrs["bill"]["amount"]["currency"],
            str(attrs["bill"]["amount"]["value"]),
            str(attrs["bill"]["bill_id"].id),
            attrs["bill"]["site_id"],
            attrs["bill"]["status"]["value"],
        )
        if expected_hmac != attrs["hmac"]:
            self.fail("mismatch_hmac")
        return attrs
