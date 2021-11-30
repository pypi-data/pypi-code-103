import json
import logging

import requests
from celery import current_app
from django.apps import apps
from django.db import models
from django.db.models import F
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.module_loading import import_string
from rest_framework.utils.encoders import JSONEncoder

from whisperer.client import WebhookClient
from whisperer.events import registry
from whisperer.exceptions import (
    EventAlreadyDelivered,
    UnknownEventType,
    WebhookEventDoesNotExist,
)
from whisperer.utils import LockTask

TASK_RETRY_COUNT = 10
MAX_RETRY_COUNT = 18
logger = logging.getLogger(__name__)


def get_natural_key(instance):
    from django.contrib.contenttypes.models import ContentType

    content_type = ContentType.objects.get_for_model(instance)
    return content_type.natural_key()


@current_app.task(bind=True, max_retries=TASK_RETRY_COUNT, base=LockTask)
def deliver_event_task(
    self,
    hook_id,
    event_type,
    event_uuid=None,
    instance=None,
    app_label=None,
    model_name=None,
    pk=None,
    retry=True,
    **kwargs
):
    from whisperer.models import Webhook

    hook = Webhook.objects.get(pk=hook_id)
    if not event_uuid and not instance and app_label and model_name and pk:
        model_class = apps.get_model(app_label, model_name)
        instance = model_class.objects.get(pk=pk)

    webhook_event, response = _deliver_event(
        hook, instance, event_type, event_uuid=event_uuid
    )

    if not response.ok:
        self.request.kwargs['event_uuid'] = webhook_event.uuid
        webhook_event.refresh_from_db(fields=['retry_count'])
        webhook_event_retry_count = webhook_event.retry_count or 1
        if (
            self.request.retries >= TASK_RETRY_COUNT
            or webhook_event_retry_count >= MAX_RETRY_COUNT
            or not retry
        ):
            return

        self.retry(countdown=hook.countdown.get_value(self.request.retries))


def _deliver_event(hook, instance, event_type, event_uuid=None, force=False):
    from django.contrib.contenttypes.models import ContentType

    from whisperer.models import WebhookEvent

    if event_type not in registry:
        raise UnknownEventType()

    if event_uuid:
        try:
            webhook_event = WebhookEvent.objects.get(uuid=event_uuid)
            payload = webhook_event.request_payload
            if webhook_event.delivered and not force:
                raise EventAlreadyDelivered()
        except WebhookEvent.DoesNotExist:
            raise WebhookEventDoesNotExist()
    else:
        webhook_event = WebhookEvent(webhook=hook, retry_count=0)
        event_class = registry[event_type]
        event = event_class()
        serialize_instance = event.serialize(instance)
        payload = {
            'event': {'type': event_type, 'uuid': webhook_event.uuid.hex},
            'payload': serialize_instance,
        }

    request_datetime = timezone.now()
    response = requests.Response()
    try:
        client = WebhookClient(event_type=event_type, payload=payload)
        response = client.send_payload(
            target_url=hook.target_url,
            payload=payload,
            secret_key=hook.secret_key,
            additional_headers=hook.additional_headers,
            auth_config=hook.config.get('auth'),
        )
    except requests.exceptions.RequestException as exc:
        response.status_code = (exc.response and exc.response.status_code) or 500
        response._content = exc
    except Exception as exc:
        response._content = ''
        response.status_code = 500
        logger.exception(exc)
    finally:
        webhook_event.request_payload = json.loads(json.dumps(payload, cls=JSONEncoder))
        webhook_event.response_content = response.content
        webhook_event.response_http_status = response.status_code
        if isinstance(instance, (models.Model, models.base.ModelBase)):
            webhook_event.object_id = instance.pk
            webhook_event.content_object = instance
            webhook_event.content_type = ContentType.objects.get_for_model(
                instance._meta.model
            )
        if 200 <= response.status_code < 300:
            webhook_event.delivered = True
        else:
            webhook_event.delivered = False
        webhook_event.request_datetimes.insert(0, request_datetime)
        webhook_event.retry_count = (
            Coalesce(F('retry_count') + 1, len(webhook_event.request_datetimes))
            if webhook_event.pk
            else 1
        )
        webhook_event.save()

    if hook.callback:
        callback_function = import_string(hook.callback)
        callback_function(response, event_type, instance, payload)

    return webhook_event, response


def deliver_event(instance, event_type, async_=True, event_uuid=None):
    from whisperer.models import Webhook

    hooks = Webhook.objects.filter(event_type=event_type, is_active=True)
    for hook in hooks:
        if not async_:
            _deliver_event(hook, instance, event_type, event_uuid)
            continue
        if isinstance(instance, (models.Model, models.base.ModelBase)):
            app_label, model_name = get_natural_key(instance)
            deliver_event_task.delay(
                hook_id=hook.pk,
                event_type=event_type,
                app_label=app_label,
                model_name=model_name,
                pk=instance.pk,
                event_uuid=event_uuid,
            )
        elif isinstance(instance, dict):
            deliver_event_task.delay(
                hook_id=hook.pk,
                event_type=event_type,
                instance=instance,
                event_uuid=event_uuid,
            )
        else:
            raise NotImplementedError()


@current_app.task()
def undelivered_event_scanner():
    from whisperer.models import WebhookEvent

    undelivered_events = WebhookEvent.objects.filter(
        retry_count__gte=TASK_RETRY_COUNT + 1,
        retry_count__lte=MAX_RETRY_COUNT,
        delivered=False,
    ).all()

    for undelivered_event in undelivered_events:
        if undelivered_event.is_retry_allowed:
            deliver_event_task.delay(
                hook_id=undelivered_event.webhook_id,
                event_type=undelivered_event.webhook.event_type,
                event_uuid=undelivered_event.uuid,
                retry=False,
            )
