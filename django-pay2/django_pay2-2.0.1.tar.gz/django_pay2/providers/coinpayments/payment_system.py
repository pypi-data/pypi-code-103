from django_pay2.payment_methods import PaymentMethodType
from django_pay2.providers import register
from django_pay2.providers.base import PaymentSystem

from .api import get_api


@register
class CoinPayments(PaymentSystem):
    name = "coinpayments"
    verbose_name = "CoinPayments"
    method_type = PaymentMethodType.REDIRECT

    def generate_payment_method(
        self, payment_id, amount, currency, buyer_email, request, **kwargs
    ):
        api = get_api()
        return api.generate_payment_method(
            request, amount, currency, payment_id, buyer_email
        )
