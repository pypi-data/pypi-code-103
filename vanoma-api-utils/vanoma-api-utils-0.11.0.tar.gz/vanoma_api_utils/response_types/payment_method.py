from typing import Optional
from uuid import UUID
from datetime import datetime
from dateutil import parser
from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json  # type: ignore
from dataclasses_json.api import LetterCase  # type: ignore

"""
TODO: Use DataClassJsonMixin to improve mypy. 
TODO: There's currently a bug in this class because it doesn't recognize letter_case.
"""


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Extra:
    phone_number: str
    short_code: Optional[str]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PaymentMethod:
    payment_method_id: UUID
    customer_id: UUID
    type: str
    is_default: bool
    is_hidden: bool
    extra: Extra
    created_at: datetime = field(metadata=config(decoder=parser.isoparse))
    updated_at: datetime = field(metadata=config(decoder=parser.isoparse))


def parse_payment_method(json: str) -> PaymentMethod:
    return PaymentMethod.from_json(json)  # type: ignore
