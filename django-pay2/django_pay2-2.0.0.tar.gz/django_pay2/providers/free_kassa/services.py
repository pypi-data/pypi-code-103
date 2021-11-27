from .serializers import FreeKassaNotifySerializer


def handle_notify(data):
    serializer = FreeKassaNotifySerializer(
        data={
            "merchant_id": data.get("MERCHANT_ID"),
            "amount": data.get("AMOUNT"),
            "order": data.get("MERCHANT_ORDER_ID"),
            "sign": data.get("SIGN"),
        }
    )
    serializer.is_valid(raise_exception=True)
    payment = serializer.validated_data["order"]
    payment.accept()
    return payment
