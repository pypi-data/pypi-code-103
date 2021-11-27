from rest_framework import serializers

from django_pay2.models import Payment

from .api import get_api


class PerfectMoneyNotifySerializer(serializers.Serializer):
    payee_account = serializers.CharField()
    payment_id = serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all())
    payment_amount = serializers.DecimalField(decimal_places=2, max_digits=20)
    payment_units = serializers.CharField()
    payment_batch_num = serializers.CharField()
    payer_account = serializers.CharField()
    timestamp = serializers.CharField()
    sign = serializers.CharField()

    default_error_messages = {
        "incorrect_sign": "Incorrect sign",
        "mismatch_payment": "Mismatch payment",
        "incorrect_amount": "Incorrect amount",
    }

    def to_internal_value(self, data):
        new_data = {
            "payee_account": data.get("PAYEE_ACCOUNT"),
            "payment_id": data.get("PAYMENT_ID"),
            "payment_amount": data.get("PAYMENT_AMOUNT"),
            "payment_units": data.get("PAYMENT_UNITS"),
            "payment_batch_num": data.get("PAYMENT_BATCH_NUM"),
            "payer_account": data.get("PAYER_ACCOUNT"),
            "timestamp": data.get("TIMESTAMPGMT"),
            "sign": data.get("V2_HASH"),
        }
        return super().to_internal_value(new_data)

    def validate(self, attrs):
        if attrs["payment_amount"] != attrs["payment_id"].amount:
            self.fail("incorrect_amount")

        api = get_api()
        expected_sign = api.calculate_sign(
            attrs["payment_id"].id,
            attrs["payment_amount"],
            attrs["payment_units"],
            attrs["payment_batch_num"],
            attrs["payer_account"],
            attrs["timestamp"],
        )
        if expected_sign != attrs["sign"]:
            self.fail("incorrect_sign")

        return attrs
