from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from whisperer.countdown import countdown_classes
from whisperer.models import Webhook, WebhookEvent
from whisperer.validators import countdown_kwargs_serializers


class RetryCountdownConfigSerializer(serializers.Serializer):
    choice = serializers.CharField()
    kwargs = serializers.JSONField()

    def validate_choice(self, choice):
        if not (choice in countdown_kwargs_serializers and choice in countdown_classes):
            raise ValidationError('"%s" is not a valid choice.' % choice)
        return choice

    def validate(self, attrs):
        serializer_class = countdown_kwargs_serializers[attrs['choice']]
        serializer = serializer_class(data=attrs['kwargs'])
        if not serializer.is_valid():
            raise ValidationError({'kwargs': serializer.errors})
        attrs['kwargs'] = serializer.validated_data
        return attrs


class WebhookSerializer(serializers.ModelSerializer):
    retry_countdown_config = RetryCountdownConfigSerializer()

    class Meta:
        model = Webhook
        exclude = ('user',)


class WebhookEventSerializer(serializers.ModelSerializer):
    webhook = WebhookSerializer()

    class Meta:
        model = WebhookEvent
        fields = '__all__'
