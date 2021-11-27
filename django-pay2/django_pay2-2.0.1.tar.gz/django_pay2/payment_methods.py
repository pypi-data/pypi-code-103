import enum
from dataclasses import dataclass
from enum import auto
from typing import Dict


class PaymentMethodType(enum.Enum):
    REDIRECT = auto()
    FORM = auto()


class PaymentMethod:
    method: str


@dataclass
class PaymentRedirect(PaymentMethod):
    method = "redirect"
    url: str


@dataclass
class PaymentForm(PaymentMethod):
    method = "form"
    action: str
    fields: Dict[str, str]
