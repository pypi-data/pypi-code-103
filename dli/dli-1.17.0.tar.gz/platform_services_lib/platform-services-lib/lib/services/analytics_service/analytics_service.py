#
# Copyright (C) 2019 IHS Markit.
# All Rights Reserved
#

try:
    # these are only present for services, not for the SDK, and we do not wish to impose these in requirements.txt
    from injector import inject
except ModuleNotFoundError:
    # set up an Identity decorator for @inject
    def inject(function):  # type: ignore
        def wrapper(*args, **kwargs):
            return function(*args, *kwargs)
        return wrapper
except:
    pass

from ..analytics_service.model import AnalyticsEvent
from ..ga_service.ga_service import GoogleAnalyticsService


class AnalyticsService:

    @inject
    def __init__(self, analytics_service: GoogleAnalyticsService):
        self._analytics_service = analytics_service

    def process(self, action_info: AnalyticsEvent) -> None:
        if not action_info:
            return

        body = self._analytics_service.create_message_body(action_info)
        self._analytics_service.send_message(body)
