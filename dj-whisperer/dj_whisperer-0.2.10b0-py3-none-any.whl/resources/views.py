from rest_framework import viewsets

from whisperer.models import Webhook, WebhookEvent
from whisperer.resources.filters import WebhookEventFilter, WebhookFilter
from whisperer.resources.serializers import WebhookEventSerializer, WebhookSerializer
from whisperer.services import WebhookService


class WebhookViewSet(viewsets.ModelViewSet):
    queryset = Webhook.objects.all()
    serializer_class = WebhookSerializer
    service = WebhookService()
    filter_class = WebhookFilter

    def get_queryset(self):
        queryset = super(WebhookViewSet, self).get_queryset()
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.instance = self.service.register_webhook(
            user, **serializer.validated_data
        )

    def perform_update(self, serializer):
        user = self.request.user
        self.service.update_webhook(
            serializer.instance, user=user, **serializer.validated_data
        )

    def perform_destroy(self, instance):
        self.service.delete_webhook(instance)


class WebhookEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WebhookEvent.objects.all()
    filter_class = WebhookEventFilter
    serializer_class = WebhookEventSerializer

    def get_queryset(self):
        queryset = super(WebhookEventViewSet, self).get_queryset()
        return queryset.filter(webhook__user=self.request.user)
