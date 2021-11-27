from django.conf import settings

from .api import TinkoffApi


def get_tinkoff_api() -> TinkoffApi:
    return TinkoffApi(
        settings.TINKOFF_TERMINAL_KEY,
        settings.TINKOFF_PASSWORD,
    )
