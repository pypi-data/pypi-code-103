from decimal import Decimal as D
from uuid import UUID

from django_pay2.payment_methods import PaymentMethodType
from django_pay2.providers import register
from django_pay2.providers.base import PaymentSystem

from .api import get_api


@register
class PerfectMoney(PaymentSystem):
    name = "perfect_money"
    verbose_name = "PerfectMoney"
    method_type = PaymentMethodType.FORM

    def generate_payment_method(
        self, payment_id: UUID, amount: D, request, currency, **kwargs
    ):
        api = get_api()
        return api.generate_payment_method(request, amount, currency, payment_id)
