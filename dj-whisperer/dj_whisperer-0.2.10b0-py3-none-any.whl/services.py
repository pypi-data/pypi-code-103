from whisperer.exceptions import WebhookAlreadyRegistered
from whisperer.models import Webhook


class WebhookService(object):
    def register_webhook(self, user, *args, **kwargs):
        event_type = kwargs.get('event_type')
        target_url = kwargs.get('target_url')
        try:
            Webhook.objects.get(user=user, target_url=target_url, event_type=event_type)
            raise WebhookAlreadyRegistered()
        except Webhook.DoesNotExist:
            pass
        webhook = Webhook(user=user)
        for attr, value in kwargs.items():
            setattr(webhook, attr, value)
        webhook.save()
        return webhook

    def update_webhook(self, webhook, user, *args, **kwargs):
        webhook.user = user
        target_url = kwargs.get('target_url', webhook.target_url)
        event_type = kwargs.get('event_type', webhook.event_type)
        try:
            Webhook.objects.exclude(id=webhook.id).get(
                user=user, target_url=target_url, event_type=event_type
            )
            raise WebhookAlreadyRegistered()
        except Webhook.DoesNotExist:
            pass

        for attr, value in kwargs.items():
            setattr(webhook, attr, value)
        webhook.save(update_fields=kwargs.keys())
        return webhook

    def delete_webhook(self, webhook):
        webhook.is_active = False
        webhook.save(update_fields=['is_active'])
