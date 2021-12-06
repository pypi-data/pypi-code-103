from django.conf import settings
from rest_framework import throttling
from django.core.exceptions import ImproperlyConfigured


class SecurityRateThrottle(throttling.SimpleRateThrottle):
    """Обязательная бликировка после каждого запроса"""

    security_throttle_anon = 'security_throttle_anon'
    security_throttle_user = 'security_throttle_user'

    def __init__(self):
        self._anon_rate = 5  # Количество секунд на 1 запрос для анонимных
        self._user_rate = 10  # Количество секунд на 1 запрос для авторизованных
        self._rate = None

    def get_rate(self):
        raise NotImplemented

    @property
    def rate(self):
        if not getattr(self, '_rate', None):
            msg = ("You must set either `.rate` for '%s' throttle" %
                   self.__class__.__name__)
            raise ImproperlyConfigured(msg)
        return int(self._rate)

    def set_rate(self, request, view):
        if request.user.is_authenticated:
            view_rate = getattr(view, self.security_throttle_user, None)
            self._rate = view_rate if view_rate and view_rate >= 1 else self._user_rate
        else:
            view_rate = getattr(view, self.security_throttle_anon, None)
            self._rate = view_rate if view_rate and view_rate >= 1 else self._anon_rate

    def parse_rate(self, rate):
        return 1, rate

    def get_cache_key(self, request, view):
        try:
            scope = f'{view.__class__.__name__}_{view.action}'
        except AttributeError:
            scope = f'{view.__class__.__name__}'

        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            'scope': scope,
            'ident': ident
        }

    def allow_request(self, request, view):
        if settings.DEBUG:
            return True
        self.set_rate(request, view)
        rate = self.rate
        self.num_requests, self.duration = self.parse_rate(rate)
        return super().allow_request(request, view)
