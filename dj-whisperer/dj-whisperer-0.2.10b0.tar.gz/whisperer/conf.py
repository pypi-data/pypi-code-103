from django.conf import settings as django_settings

DEFAULT_SETTINGS = {
    "WHISPERER_REQUEST_TIMEOUT": 10,
}


class Settings(object):
    def __getattr__(self, item):
        if item in DEFAULT_SETTINGS:
            return getattr(django_settings, item, DEFAULT_SETTINGS[item])
        raise AttributeError


settings = Settings()
