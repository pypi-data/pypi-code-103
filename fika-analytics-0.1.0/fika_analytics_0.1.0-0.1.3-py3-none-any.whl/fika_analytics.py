from mixpanel import Mixpanel
from mixpanel_async import AsyncBufferedConsumer

# from ...core.config import cnf
from .analytics_constants import (DEVELOPMENT_MIXPANEL_TOKEN,
                                  PRODUCTION_MIXPANEL_TOKEN,
                                  STAGING_MIXPANEL_TOKEN)
from .analytics_event import AnalyticsEvent
from .user_property import UserPropertyUpdate


# MIXPANEL_TOKEN = cnf.MIXPANEL_TOKEN
'''
FikaAnalytics wraps the analytics library, Mixpanel. This allows us to later
swap out the underlying analytics libraries or
implement our own without changing the way it is being
used in other points of the code.
'''


class FikaAnalytics:
    def __init__(self, environment):
        self._mp = None
        # Numbers and settings should be adjusted to see what makes sense

        self.consumer = AsyncBufferedConsumer(max_size=100)

        self.should_enable_logging = True

        # assign env for mixpanel
        # self._mp = Mixpanel(MIXPANEL_TOKEN, consumer=self.consumer)
        if environment == "development":
            self._mp = Mixpanel(DEVELOPMENT_MIXPANEL_TOKEN, consumer=self.consumer)
        elif environment == "staging":
            self._mp = Mixpanel(STAGING_MIXPANEL_TOKEN, consumer=self.consumer)
        else:
            self._mp = Mixpanel(PRODUCTION_MIXPANEL_TOKEN, consumer=self.consumer)
            # self.should_enable_logging = False

    def track(self, analytics_event: AnalyticsEvent) -> None:
        self._mp.track(
            analytics_event.user_id,
            analytics_event.event_name,
            analytics_event.event_properties.dict()
        )

    def update_user_profile(self, user_property: UserPropertyUpdate) -> None:
        self._mp.people_set(user_property.user_id, properties=user_property.user_properties.dict())

    def flush(self, is_async: bool = True):
        self.consumer.flush(async_=is_async)
