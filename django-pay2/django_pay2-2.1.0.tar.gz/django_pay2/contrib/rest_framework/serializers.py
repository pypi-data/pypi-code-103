from rest_framework import serializers


class PaymentRedirectSerializer(serializers.Serializer):
    method = serializers.CharField()
    url = serializers.CharField()


class PaymentFormSerializer(serializers.Serializer):
    method = serializers.CharField()
    action = serializers.CharField()
    fields = serializers.DictField()
