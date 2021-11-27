from decimal import Decimal as D
from typing import Any

from django_pay2.providers import get_payment_system


def create_payment(amount: D, receiver: Any, payment_system_name: str, **kwargs):
    try:
        payment_system = get_payment_system(payment_system_name)
    except KeyError:
        raise AssertionError(
            f"Payment system with name={payment_system_name} does not exist"
        )

    return payment_system.create_payment(receiver=receiver, amount=amount, **kwargs)
