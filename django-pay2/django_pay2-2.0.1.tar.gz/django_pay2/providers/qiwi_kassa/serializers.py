import logging

from rest_framework import serializers

from django_pay2.models import Payment
from django_pay2.utils import HmacDefault, MappingFieldsMixin

from .api import get_api

logger = logging.getLogger(__name__)


class StatusSerializer(serializers.Serializer):
    value = serializers.CharField()


class AmountSerializer(serializers.Serializer):
    value = serializers.DecimalField(max_digits=20, decimal_places=2)
    currency = serializers.CharField()


class QiwiPaymentSerializer(MappingFieldsMixin, serializers.Serializer):
    mapping_keys = {
        "payment_id": "paymentId",
        "bill_id": "billId",
        "created_datetime": "createdDateTime",
    }

    payment_id = serializers.CharField()
    bill_id = serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all())
    amount = AmountSerializer()
    status = StatusSerializer()
    created_datetime = serializers.CharField()

    default_error_messages = {"mismatched_amount": "Mismatched amount"}

    def validate(self, attrs):
        attrs = super().validate(attrs)
        bill = attrs["bill_id"]
        if bill.amount != attrs["amount"]["value"]:
            self.fail("mismatched_amount")
        return attrs


class QiwiKassaNotifySerializer(serializers.Serializer):
    payment = QiwiPaymentSerializer()
    hmac = serializers.HiddenField(default=HmacDefault())

    default_error_messages = {"mismatch_hmac": "Mismatch HMAC"}

    def validate(self, attrs):
        attrs = super().validate(attrs)
        expected_hmac = get_api().create_hmac(
            payment_id=attrs["payment"]["payment_id"],
            created_datetime=attrs["payment"]["created_datetime"],
            amount=attrs["payment"]["amount"]["value"],
        )
        if expected_hmac != attrs["hmac"]:
            logger.info(f"Mismatch hmac: expected={expected_hmac} got={attrs['hmac']}")
            self.fail("mismatch_hmac")
        return attrs
