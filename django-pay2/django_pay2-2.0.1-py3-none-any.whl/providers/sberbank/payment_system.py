from decimal import Decimal as D
from typing import Optional
from uuid import UUID

from django_pay2.payment_methods import PaymentMethodType
from django_pay2.providers import register
from django_pay2.providers.base import PaymentSystem
from django_pay2.settings import payment_settings

from .api import SberbankApi


def get_api() -> SberbankApi:
    return SberbankApi(
        username=payment_settings.SBERBANK.username,
        password=payment_settings.SBERBANK.password,
    )


@register
class Sberbank(PaymentSystem):
    name = "sberbank"
    verbose_name = "Сбербанк"
    method_type = PaymentMethodType.REDIRECT

    def generate_payment_method(
        self,
        payment_id: UUID,
        amount: D,
        desc: str,
        return_url: Optional[str] = None,
        fail_url: Optional[str] = None,
        page_view: Optional[str] = None,
        phone: Optional[str] = None,
        **kwargs
    ):
        return_url = return_url or payment_settings.SBERBANK.return_url
        fail_url = fail_url or payment_settings.SBERBANK.fail_url
        api = get_api()
        return api.register_payment(
            order_num=str(payment_id),
            amount=str(amount),
            return_url=return_url,
            fail_url=fail_url,
            description=desc,
            page_view=page_view,
            phone=phone,
        )
