from django_pay2.settings import payment_settings

from .api import PayeerApi


def get_payeer_api() -> PayeerApi:
    return PayeerApi(
        account=payment_settings.PAYEER.account,
        api_id=payment_settings.PAYEER.api_id,
        api_password=payment_settings.PAYEER.api_password,
        secret_key=payment_settings.PAYEER.secret_key,
        shop_id=payment_settings.PAYEER.shop_id,
    )
