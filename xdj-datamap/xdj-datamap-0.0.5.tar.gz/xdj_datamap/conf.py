from django.conf import settings

from xdj_datamap.defaults import TABLE_PREFIX


class Settings:

    @property
    def TABLE_PREFIX(self):
        return getattr(settings, "TABLE_PREFIX", TABLE_PREFIX)


conf = Settings()
