from decimal import Decimal as D
from uuid import UUID

from django_pay2.exceptions import CreatePaymentError
from django_pay2.payment_methods import PaymentMethodType
from django_pay2.providers import register
from django_pay2.providers.base import PaymentSystem

from .exceptions import PayeerError
from .functions import get_payeer_api


@register
class Payeer(PaymentSystem):
    name = "payeer"
    verbose_name = "Payeer"
    method_type = PaymentMethodType.REDIRECT

    def generate_payment_method(
        self, payment_id: UUID, amount: D, currency, desc, **kwargs
    ):
        try:
            api = get_payeer_api()
            return api.create_payment(str(payment_id), amount, currency, desc)
        except PayeerError as exc:
            raise CreatePaymentError(str(exc))
