from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_pay2.providers.base import PaymentSystem


_PAYMENT_SYSTEMS = {}


def register(payment_system):
    assert (
        payment_system.name
        and payment_system.verbose_name
        and payment_system.method_type
    ), f"Define `name`, `verbose_name` and `method_type` attributes for {payment_system}"

    _PAYMENT_SYSTEMS[payment_system.name] = payment_system()

    return payment_system


def get_payment_system(name: str) -> "PaymentSystem":
    return _PAYMENT_SYSTEMS[name]
