from django.contrib import admin

from whisperer.models import Webhook, WebhookEvent


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_active", "event_type")


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ("uuid", "webhook", "delivered", "response_http_status")
