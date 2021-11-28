import hashlib
from dataclasses import dataclass
from typing import Iterable, Optional, SupportsInt

import requests

from django_pay2.utils import clear_none

from .constants import (
    Languages,
    PaymentMethods,
    PaymentObjects,
    PayTypes,
    Taxations,
    Taxes,
)
from .exceptions import TinkoffNetworkError, TinkoffResponseError


def _bool_to_str(a_bool):
    return str(a_bool).lower()


def _to_json_str(value):
    if isinstance(value, bool):
        return _bool_to_str(value)
    return str(value)


class TinkoffApi:
    def __init__(self, terminal_key: str, password: str):
        self.terminal_key = terminal_key
        self.password = password

    def init_payment(
        self,
        amount_rub: SupportsInt,
        order_id: str,
        ip: Optional[str] = None,
        description: Optional[str] = None,
        lang: Optional[Languages] = None,
        notification_url: Optional[str] = None,
        success_url: Optional[str] = None,
        fail_url: Optional[str] = None,
        pay_type: Optional[PayTypes] = None,
        items: Optional[Iterable["TinkoffOrderItem"]] = None,
        client_email: Optional[str] = None,
        client_phone: Optional[str] = None,
        email_company: Optional[str] = None,
        taxation: Optional[Taxations] = None,
    ):
        token_data = clear_none(
            {
                "TerminalKey": self.terminal_key,
                "Amount": int(amount_rub * 100),
                "OrderId": order_id,
                "IP": ip,
                "Description": description,
                "Language": lang,
                "NotificationURL": notification_url,
                "SuccessURL": success_url,
                "FailURL": fail_url,
                "PayType": pay_type,
                "Receipt": clear_none(
                    {
                        "Items": [
                            clear_none(
                                {
                                    "Name": item.name,
                                    "Quantity": item.quantity,
                                    "Amount": int(item.amount_rub * 100),
                                    "Price": int(item.price_rub * 100),
                                    "PaymentMethod": item.payment_method,
                                    "PaymentObject": item.payment_object,
                                    "Tax": item.tax,
                                }
                            )
                            for item in items
                        ],
                        "Email": client_email,
                        "Phone": client_phone,
                        "EmailCompany": email_company,
                        "Taxation": taxation,
                    }
                )
                if items is not None
                else None,
            }
        )
        data = {
            **token_data,
            "Token": self.calculate_token(token_data),
        }
        raw_response = requests.post("https://securepay.tinkoff.ru/v2/Init", json=data)
        if not raw_response.ok:
            raise TinkoffNetworkError(raw_response.status_code, raw_response.text)

        response = InitResponse(raw_response.json())
        if not response.is_success:
            raise TinkoffResponseError(
                response.error_code, response.message, response.details
            )
        return response

    def calculate_token(self, data):
        prep_data = {
            k: v for k, v in data.items() if k not in ["Receipt", "Data", "Token"]
        }
        prep_data["Password"] = self.password
        sorted_data = {k: prep_data[k] for k in sorted(prep_data.keys())}
        hash_str = "".join(_to_json_str(v) for v in sorted_data.values())
        hash_obj = hashlib.sha256(hash_str.encode("utf-8"))
        return hash_obj.hexdigest()


class InitResponse:
    def __init__(self, raw_data):
        self.is_success: str = raw_data["Success"]
        self.payment_id: int = raw_data.get("PaymentId")
        self.error_code: str = raw_data["ErrorCode"]
        self.payment_url: Optional[str] = raw_data.get("PaymentURL")
        self.message: Optional[str] = raw_data.get("Message")
        self.details: Optional[str] = raw_data.get("Details")


@dataclass
class TinkoffOrderItem:
    name: str
    quantity: int
    amount_rub: SupportsInt
    price_rub: SupportsInt
    tax: Taxes
    payment_method: Optional[PaymentMethods] = None
    payment_object: Optional[PaymentObjects] = None

    def serialize(self):
        return clear_none(
            {
                "Name": self.name,
                "Quantity": self.quantity,
                "Amount": int(self.amount_rub * 100),
                "Price": int(self.price_rub * 100),
                "PaymentMethod": self.payment_method,
                "PaymentObject": self.payment_object,
                "Tax": self.tax,
            }
        )
