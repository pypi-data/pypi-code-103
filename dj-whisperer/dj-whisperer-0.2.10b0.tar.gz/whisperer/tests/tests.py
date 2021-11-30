import random
import uuid
from datetime import timedelta

import mock
import requests
import requests_mock
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from django.utils import timezone
from model_mommy import mommy

from whisperer.countdown import (
    ExponentialRetryCountdown,
    FixedRetryCountdown,
    LinearRetryCountdown,
    RandomRetryCountdown,
)
from whisperer.exceptions import WebhookAlreadyRegistered
from whisperer.models import Webhook, WebhookEvent
from whisperer.resources.serializers import WebhookSerializer
from whisperer.services import WebhookService
from whisperer.tasks import (
    MAX_RETRY_COUNT,
    TASK_RETRY_COUNT,
    deliver_event,
    deliver_event_task,
    undelivered_event_scanner,
)
from whisperer.tests.models import Address, Customer, Order
from whisperer.utils import LockTask


class WebhookTestCase(TestCase):
    def setUp(self):
        self.user = mommy.make(User, username="test_user")
        self.service = WebhookService()

    def test_register_webhook(self):
        webhook = mommy.prepare(
            Webhook,
            user=self.user,
            target_url="http://example.com/order_create",
            secret_key="secret",
            event_type="order-created",
            retry_countdown_config={"choice": "exponential", "kwargs": {"base": 2}},
        )

        serializer = WebhookSerializer(webhook)
        serializer = WebhookSerializer(data=serializer.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        webhook = self.service.register_webhook(
            user=self.user, **serializer.validated_data
        )
        self.assertEqual(webhook.event_type, "order-created")

        with self.assertRaises(WebhookAlreadyRegistered):
            self.service.register_webhook(user=self.user, **serializer.validated_data)

    def test_update_webhook(self):
        webhook = mommy.prepare(
            Webhook,
            user=self.user,
            target_url="http://example2.com/order_create",
            secret_key="secret",
            event_type="order-created",
            retry_countdown_config={"choice": "exponential", "kwargs": {"base": 2}},
        )

        serializer = WebhookSerializer(webhook)
        serializer = WebhookSerializer(data=serializer.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        webhook_created = self.service.register_webhook(
            user=self.user, **serializer.validated_data
        )

        update_data = {
            "target_url": "http://example3.com/order_update",
            "event_type": "order-update",
            "retry_countdown_config": {
                "choice": "linear",
                "kwargs": {"base": 1 * 60, "limit": 5 * 60},
            },
        }
        webhook_updated = self.service.update_webhook(
            webhook_created, self.user, **update_data
        )

        self.assertNotEqual(webhook.target_url, webhook_updated.target_url)
        self.assertNotEqual(webhook.event_type, webhook_updated.event_type)

        self.assertEqual(webhook_updated.target_url, update_data["target_url"])
        self.assertEqual(webhook_updated.event_type, "order-update")

    def test_update_webhook_with_already_registered_one(self):
        webhook = mommy.make(
            Webhook,
            user=self.user,
            target_url="http://example2.com/order_create",
            secret_key="secret",
            event_type="order-created",
            retry_countdown_config={"choice": "exponential", "kwargs": {"base": 2}},
        )

        mommy.make(
            Webhook,
            user=self.user,
            target_url="http://example2.com/order_create",
            secret_key="secret",
            event_type="order-update",
            retry_countdown_config={"choice": "exponential", "kwargs": {"base": 2}},
        )

        update_data = {"target_url": webhook.target_url, "event_type": "order-update"}

        with self.assertRaises(WebhookAlreadyRegistered):
            self.service.update_webhook(webhook, self.user, **update_data)

        del update_data["target_url"]

        with self.assertRaises(WebhookAlreadyRegistered):
            self.service.update_webhook(webhook, self.user, **update_data)

        update_data = {
            "retry_countdown_config": {
                "choice": "linear",
                "kwargs": {"base": 1 * 60, "limit": 10 * 60},
            },
        }

        webhook_updated = self.service.update_webhook(webhook, self.user, **update_data)
        self.assertEqual(
            webhook_updated.retry_countdown_config["kwargs"],
            update_data["retry_countdown_config"]["kwargs"],
        )

    def test_delete_webhook(self):
        webhook = mommy.make(Webhook, is_active=True)
        self.service.delete_webhook(webhook)
        webhook.refresh_from_db()
        self.assertFalse(webhook.is_active)


@override_settings(CELERY_ALWAYS_EAGER=True)
class WhispererEventTestCase(TestCase):
    def setUp(self):
        self.target_url = "http://example.com/order_create"
        self.user = mommy.make(User, username="test_user")

        self.webhook = mommy.make(
            Webhook,
            user=self.user,
            target_url=self.target_url,
            secret_key="secret",
            event_type="order-created",
            retry_countdown_config={"choice": "exponential", "kwargs": {"base": 2}},
        )
        self.target_url2 = "http://example.com/auth_order_update"
        self.webhook2 = mommy.make(
            Webhook,
            user=self.user,
            target_url=self.target_url2,
            secret_key="secret",
            event_type="order-updated",
            retry_countdown_config={"choice": "exponential", "kwargs": {"base": 2}},
            config={
                "auth": {
                    "username": "username",
                    "password": "123",
                    "auth_type": "basic",
                }
            },
        )
        self.target_url3 = "http://example.com/test_order_update"
        self.webhook3 = mommy.make(
            Webhook,
            user=self.user,
            target_url=self.target_url3,
            secret_key="secret",
            event_type="order-updated",
            retry_countdown_config={"choice": "exponential", "kwargs": {"base": 2}},
            config={
                "auth": {
                    "auth_type": "token",
                    "url": "http://test.com",
                    "username": "username",
                    "password": "123",
                }
            },
        )

        self.customer = mommy.make(Customer)
        self.address = mommy.make(Address)
        self.order = mommy.prepare(
            Order,
            customer=self.customer,
            address=self.address,
            number="1",
            amount="1",
            discount_amount="1",
            shipping_amount="1",
        )

    def test_deliver_event(self):
        with requests_mock.Mocker() as mock:
            mock.register_uri(
                "POST", self.target_url, text="Order Created", status_code=200
            )
            self.order.save()
            webhook_events = WebhookEvent.objects.all()
            self.assertEqual(len(webhook_events), 1)
            self.assertTrue(webhook_events[0].delivered)

    def test_deliver_event_sync_with_event_uuid(self):
        webhookevent = mommy.make(
            WebhookEvent,
            modified_date=timezone.now(),
            created_date=timezone.now(),
            request_payload={},
            retry_count=TASK_RETRY_COUNT,
            delivered=False,
            webhook=self.webhook,
        )
        with requests_mock.Mocker() as mock:
            mock.register_uri(
                "POST", self.webhook.target_url, text="Order Created", status_code=200
            )
            deliver_event(
                self.order, "order-created", async_=False, event_uuid=webhookevent.uuid
            )
            webhookevent.refresh_from_db()
            self.assertTrue(webhookevent.delivered)

    def test_deliver_event_async_with_event_uuid(self):
        webhookevent = mommy.make(
            WebhookEvent,
            modified_date=timezone.now(),
            created_date=timezone.now(),
            request_payload={},
            retry_count=TASK_RETRY_COUNT,
            delivered=False,
            webhook=self.webhook,
        )
        with requests_mock.Mocker() as mock:
            mock.register_uri(
                "POST", self.webhook.target_url, text="Order Created", status_code=200
            )
            deliver_event(self.order, "order-created", event_uuid=webhookevent.uuid)
            webhookevent.refresh_from_db()
            self.assertTrue(webhookevent.delivered)

    @mock.patch("requests.post")
    def test_http_error(self, post_mock):
        post_mock.side_effect = requests.exceptions.HTTPError("HTTPError")
        self.order.save()
        webhook_events = WebhookEvent.objects.all()
        self.assertEqual(len(webhook_events), 1)
        self.assertFalse(webhook_events[0].delivered)
        self.assertEqual(webhook_events[0].response_http_status, 500)
        self.assertIn("HTTPError", webhook_events[0].response_content)

    @mock.patch("requests.post")
    def test_unboundlocal_error(self, post_mock):
        post_mock.side_effect = UnboundLocalError()
        self.order.save()
        webhook_events = WebhookEvent.objects.all()
        self.assertEqual(len(webhook_events), 1)
        self.assertFalse(webhook_events[0].delivered)
        self.assertEqual(webhook_events[0].response_http_status, 500)
        self.assertIn("", webhook_events[0].response_content)

    def test_undelivered_event_scanner(self):
        date1 = timezone.now() - timedelta(days=1)
        date2 = timezone.now() - timedelta(days=4)
        webhook = mommy.make(
            Webhook,
            user=self.user,
            target_url="http://example.com/order_update",
            secret_key="secret",
            event_type="order-created",
            retry_countdown_config={"choice": "exponential", "kwargs": {"base": 2}},
        )
        # unsuitable for event scanner query because of  retry limit
        webhookevent1 = mommy.make(
            WebhookEvent,
            modified_date=timezone.now(),
            created_date=timezone.now(),
            request_payload={},
            retry_count=TASK_RETRY_COUNT,
            delivered=False,
            webhook=webhook,
        )
        # unsuitable for event scanner query because of MAX_RETRY_COUNT
        webhookevent2 = mommy.make(
            WebhookEvent,
            request_payload={},
            retry_count=MAX_RETRY_COUNT + 1,
            delivered=False,
            webhook=webhook,
        )
        # unsuitable for event scanner query because of delivered
        webhookevent3 = mommy.make(
            WebhookEvent,
            request_payload={},
            retry_count=TASK_RETRY_COUNT + 1,
            delivered=True,
            webhook=webhook,
        )

        # unsuitable for event scanner control
        #  if undelivered_event.created_date + timedelta(seconds=2 ** undelivered_event.retry_count) <= timezone.now():
        webhookevent4 = mommy.make(
            WebhookEvent,
            request_payload={},
            retry_count=15,
            delivered=False,
            webhook=webhook,
        )

        webhookevent5 = mommy.make(
            WebhookEvent,
            request_payload={},
            retry_count=TASK_RETRY_COUNT + 1,
            delivered=False,
            webhook=webhook,
        )
        WebhookEvent.objects.filter(id=webhookevent5.id).update(
            created_date=timezone.now()
            - timedelta(2 ** (webhookevent5.retry_count + 1))
        )

        with requests_mock.Mocker() as mock:
            mock.register_uri(
                "POST",
                "http://example.com/order_update",
                [
                    {"text": "Order created", "status_code": 200},
                ],
            )
            undelivered_event_scanner()
        webhookevent1.refresh_from_db()
        webhookevent2.refresh_from_db()
        webhookevent3.refresh_from_db()
        webhookevent4.refresh_from_db()
        webhookevent5.refresh_from_db()

        # only webhookevent5 send request to given mock address
        self.assertEqual(mock.call_count, 1)

        self.assertEqual(webhookevent1.retry_count, TASK_RETRY_COUNT)
        self.assertEqual(webhookevent2.retry_count, MAX_RETRY_COUNT + 1)
        self.assertEqual(webhookevent3.retry_count, TASK_RETRY_COUNT + 1)
        self.assertEqual(webhookevent4.retry_count, 15)
        self.assertEqual(webhookevent5.retry_count, TASK_RETRY_COUNT + 2)

        self.assertEqual(webhookevent1.delivered, False)
        self.assertEqual(webhookevent2.delivered, False)
        self.assertEqual(webhookevent3.delivered, True)
        self.assertEqual(webhookevent4.delivered, False)
        self.assertEqual(webhookevent5.delivered, True)

    @mock.patch.object(LockTask, "is_exists_cache_key")
    def test_deliver_event_task(self, mock_method):
        webhookevent1 = mommy.make(
            WebhookEvent,
            modified_date=timezone.now(),
            created_date=timezone.now(),
            request_payload={},
            retry_count=0,
            delivered=False,
            uuid=uuid.uuid4(),
            webhook=self.webhook,
        )
        with requests_mock.Mocker() as mock:
            mock.register_uri(
                "POST", self.target_url, [{"text": "Bad request", "status_code": 400}]
            )
            mock_method.return_value = False
            deliver_event_task.delay(
                hook_id=webhookevent1.webhook_id,
                event_type=self.webhook.event_type,
                event_uuid=webhookevent1.uuid,
            )
        webhookevent1.refresh_from_db()
        self.assertEqual(webhookevent1.retry_count, TASK_RETRY_COUNT + 1)
        self.assertFalse(webhookevent1.delivered)

        # test new event
        with requests_mock.Mocker() as mock:
            mock.register_uri(
                "POST", self.target_url, [{"text": "Bad request", "status_code": 400}]
            )
            self.order.save()

        webhookevent2 = WebhookEvent.objects.last()
        self.assertEqual(webhookevent2.retry_count, TASK_RETRY_COUNT + 1)
        self.assertFalse(webhookevent2.delivered)
        self.assertNotEqual(webhookevent2.id, webhookevent1.id)

        WebhookEvent.objects.filter(
            id__in=[
                webhookevent1.id,
                webhookevent2.id,
            ]
        ).update(created_date=timezone.now() - timedelta(seconds=2 ** 12))

        with requests_mock.Mocker() as mock:
            mock.register_uri(
                "POST",
                self.target_url,
                [{"text": "Order event received", "status_code": 200}],
            )
            WebhookEvent.objects.filter(
                id__in=[webhookevent1.id, webhookevent2.id]
            ).update(modified_date=webhookevent1.modified_date - timedelta(days=1))
            undelivered_event_scanner()

        webhookevent1.refresh_from_db()
        webhookevent2.refresh_from_db()
        self.assertEqual(webhookevent1.retry_count, TASK_RETRY_COUNT + 2)
        self.assertEqual(webhookevent2.retry_count, TASK_RETRY_COUNT + 2)
        self.assertTrue(webhookevent1.delivered)
        self.assertTrue(webhookevent2.delivered)
        self.assertEqual(webhookevent1.response_http_status, 200)
        self.assertEqual(webhookevent2.response_http_status, 200)

    @requests_mock.mock()
    @mock.patch.object(LockTask, "is_exists_cache_key")
    def test_auth_config(self, m, mock_method):
        mock_method.return_value = False
        self.order.save()
        self.order.number = "123"
        m.register_uri(
            "POST", self.target_url2, text=self._auth_test_callback, status_code=200
        )
        self.order.save()
        event = WebhookEvent.objects.filter(webhook=self.webhook2).last()
        self.assertEqual(event.response_http_status, 200)
        self.assertTrue(event.delivered)

        self.webhook2.config = {}
        self.webhook2.save()

        self.order.number = "123123"
        self.order.save()
        event = WebhookEvent.objects.filter(webhook=self.webhook2).last()
        self.assertEqual(event.response_http_status, 401)
        self.assertFalse(event.delivered)

    def _auth_test_callback(self, request, context):
        if "Authorization" not in request.headers:
            context.status_code = 401
        return ""

    @requests_mock.mock()
    @mock.patch.object(LockTask, "is_exists_cache_key")
    def test_token_auth_config(self, m, mock_method):
        mock_method.return_value = False
        self.order.save()
        self.order.number = "123"
        mock_response = {
            'key': 'testtoken123'
        }
        m.register_uri(
            "POST", self.target_url3, json=self._auth_test_callback, status_code=200
        )
        m.register_uri(
            "POST", 'http://test.com', json=mock_response, status_code=200
        )
        self.order.save()
        event = WebhookEvent.objects.filter(webhook=self.webhook3).last()
        self.assertEqual(event.response_http_status, 200)
        self.assertTrue(event.delivered)


    @requests_mock.mock()
    @mock.patch.object(LockTask, "is_exists_cache_key")
    def test_invalid_token_auth_config(self, m, mock_method):
        mock_method.return_value = False
        self.order.save()
        self.order.number = "123"
        mock_response = {
            'key': 'testtoken123'
        }
        m.register_uri(
            "POST", self.target_url3, json=self._auth_test_callback, status_code=200
        )
        m.register_uri(
            "POST", 'http://test.com', json=mock_response, status_code=500
        )
        self.order.save()
        event = WebhookEvent.objects.filter(webhook=self.webhook3).last()
        self.assertEqual(event.response_http_status, 401)

def dummy_whisperer_event_callback(response, event_type, instance, payload):
    """this function creates customer in test database"""
    mommy.make(Customer)


@override_settings(CELERY_ALWAYS_EAGER=True)
class WhispererEventCallbackTestCase(TestCase):
    def setUp(self):
        self.target_url = "http://example.com/foo_bar"
        user = mommy.make(User, username="test_user")
        mommy.make(
            Webhook,
            user=user,
            target_url=self.target_url,
            secret_key="secret",
            event_type="order-created",
            retry_countdown_config={"choice": "exponential", "kwargs": {"base": 2}},
            callback="whisperer.tests.tests.dummy_whisperer_event_callback",
        )
        customer = mommy.make(Customer)
        address = mommy.make(Address)
        self.order = mommy.prepare(
            Order,
            customer=customer,
            address=address,
            number="1",
            amount="1",
            discount_amount="1",
            shipping_amount="1",
        )

    def tearDown(self):
        Customer.objects.all().delete()

    def test_runs_callback(self):
        with requests_mock.Mocker() as mock:
            mock.register_uri(
                "POST", self.target_url, text="Request Processed", status_code=200
            )

            # before callback we have one customer
            self.assertEqual(Customer.objects.count(), 1)
            self.order.save()
            webhook_events = WebhookEvent.objects.all()
            self.assertEqual(len(webhook_events), 1)
            self.assertTrue(webhook_events[0].delivered)
            event = webhook_events.first()
            self.assertEqual(self.order.pk, event.object_id)
            self.assertEqual(
                event.content_type,
                ContentType.objects.get_for_model(self.order._meta.model),
            )
            self.assertEqual(event.content_object, self.order)

            # check callback has run
            self.assertEqual(Customer.objects.count(), 2)


class RetryCountdownTestCase(TestCase):
    def test_fixed_retry_countdown(self):
        seconds = 2 * 60
        countdown = FixedRetryCountdown(seconds=seconds)
        for _ in range(100):
            retry_count = random.randint(1, 100)
            value = countdown.get_value(retry_count)
            self.assertEqual(value, seconds)

    def test_random_retry_countdown(self):
        min_value = 1 * 60
        max_value = 10 * 60
        countdown = RandomRetryCountdown(min_value=min_value, max_value=max_value)
        for _ in range(100):
            retry_count = random.randint(1, 100)
            value = countdown.get_value(retry_count)
            self.assertTrue(min_value <= value <= max_value)

    def test_linear_retry_countdown(self):
        base = 1 * 60
        countdown = LinearRetryCountdown(base=base)
        for _ in range(100):
            retry_count = random.randint(1, 100)
            value = countdown.get_value(retry_count)
            self.assertEqual(value, base * retry_count)

        limit = 10 * 60
        countdown = LinearRetryCountdown(base=base, limit=limit)
        for _ in range(100):
            retry_count = random.randint(1, 100)
            value = countdown.get_value(retry_count)
            self.assertEqual(value, min(retry_count * base, limit))

    def test_exponential_retry_countdown(self):
        base = 2
        factor = 16
        countdown = ExponentialRetryCountdown(base=base, factor=factor)
        for _ in range(15):
            retry_count = random.randint(1, 12)
            value = countdown.get_value(retry_count)
            self.assertEqual(value, (base ** retry_count) * factor)

        limit = 20 * 60
        countdown = ExponentialRetryCountdown(base=base, factor=factor, limit=limit)
        for _ in range(15):
            retry_count = random.randint(1, 12)
            value = countdown.get_value(retry_count)
            self.assertEqual(value, min((base ** retry_count) * factor, limit))
