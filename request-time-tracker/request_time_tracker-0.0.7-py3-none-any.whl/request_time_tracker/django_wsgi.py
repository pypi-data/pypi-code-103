import logging
from typing import Any

from request_time_tracker.notifiers.cloudwatch import CloudWatchNotifier
from request_time_tracker.trackers.cache.django import DjangoCacheQueueTimeTracker
from request_time_tracker.trackers.memory import InMemoryQueueTimeTracker

logger = logging.getLogger('django.time_in_queue')


def get_django_settings(key_name, default: Any = None, fallback: Any = None):
    from django.conf import settings

    try:
        value = getattr(settings, key_name, default)
    except AttributeError:
        value = fallback or default
        logger.error('Improperly configured. {0} not configured in settings.'.format(key_name))

    return value


class LegacyQueueTimeTracker(InMemoryQueueTimeTracker):
    """
    Deprecated.
    Legacy class for backward compatibility.
    First iteration of time tracker: cloudwatch with in memory calculations
    """

    def __init__(
        self, parent_application,
        send_stats_every_seconds: int = 10,
    ):
        super().__init__(
            parent_application,
            send_stats_every_seconds=send_stats_every_seconds,
            queue_time_header_name=get_django_settings('CLOUDWATCH_QUEUE_TIME_HEADER'),
            notifier=CloudWatchNotifier(
                namespace=get_django_settings('CLOUDWATCH_QUEUE_TIME_NAMESPACE'),
                aws_access_key=get_django_settings('CLOUDWATCH_QUEUE_TIME_ACCESS_KEY'),
                aws_secret_key=get_django_settings('CLOUDWATCH_QUEUE_TIME_SECRET_KEY'),
                aws_region=get_django_settings('CLOUDWATCH_QUEUE_TIME_REGION'),
            ),
        )


class CloudWatchQueueTimeTracker(DjangoCacheQueueTimeTracker):
    """
    Cache-based tracker with cloudwatch notifier
    """
    def __init__(self, parent_application):
        super().__init__(
            parent_application,
            send_stats_every_seconds=get_django_settings('QUEUE_TIME_TRACKER_NOTIFY_EVERY_SECONDS', default=10),
            queue_time_header_name=get_django_settings('QUEUE_TIME_TRACKER_HEADER', fallback='unknown'),
            cache_name=get_django_settings('QUEUE_TIME_TRACKER_CACHE_NAME', default='unknown'),
            cache_key_prefix=get_django_settings('QUEUE_TIME_TRACKER_CACHE_KEY_PREFIX', default='queue-time-tracker'),
            notifier=CloudWatchNotifier(
                namespace=get_django_settings('QUEUE_TIME_TRACKER_CLOUDWATCH_NAMESPACE'),
                aws_access_key=get_django_settings('QUEUE_TIME_TRACKER_CLOUDWATCH_ACCESS_KEY'),
                aws_secret_key=get_django_settings('QUEUE_TIME_TRACKER_CLOUDWATCH_SECRET_KEY'),
                aws_region=get_django_settings('QUEUE_TIME_TRACKER_CLOUDWATCH_REGION'),
            ),
        )
