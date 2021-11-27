from decimal import Decimal as D
from typing import Any
from uuid import UUID

from django.urls import reverse

from django_pay2.models import Payment
from django_pay2.payment_methods import (
    PaymentForm,
    PaymentMethod,
    PaymentMethodType,
    PaymentRedirect,
)
from django_pay2.settings import payment_settings


class PaymentSystem:
    name: str
    verbose_name: str
    method_type: PaymentMethodType

    def create_payment(self, receiver: Any, amount: D, **kwargs) -> PaymentMethod:
        payment = Payment.objects.create(
            receiver=receiver, amount=amount, payment_system=self.name
        )

        if payment_settings.DEBUG_MODE:
            return self.generate_debug_payment_method(
                payment_id=payment.id, amount=amount
            )
        return self.generate_payment_method(
            payment_id=payment.id, amount=amount, **kwargs
        )

    def generate_payment_method(
        self, payment_id: UUID, amount: D, **kwargs
    ) -> PaymentMethod:
        raise NotImplementedError

    def generate_debug_payment_method(
        self, payment_id: UUID, amount: D, **kwargs
    ) -> PaymentMethod:
        if self.method_type == PaymentMethodType.REDIRECT:
            return self._generate_redirect_debug_payment(payment_id=payment_id)
        elif self.method_type == PaymentMethodType.FORM:
            return self._generate_form_debug_payment(
                payment_id=payment_id, amount=amount
            )
        raise AssertionError(f"Unexpected method_type={self.method_type}")

    def _generate_redirect_debug_payment(self, payment_id: UUID) -> PaymentRedirect:
        return PaymentRedirect(
            url=reverse("django_pay2:debug_payment", args=[payment_id])
        )

    def _generate_form_debug_payment(self, payment_id: UUID, amount: D) -> PaymentForm:
        return PaymentForm(
            action=reverse("django_pay2:debug_payment", args=[payment_id]),
            fields={"amount": str(amount)},
        )
