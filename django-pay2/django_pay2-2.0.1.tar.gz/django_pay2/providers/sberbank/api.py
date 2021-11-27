from typing import Optional
from urllib.parse import urljoin

import requests

from django_pay2.payment_methods import PaymentRedirect

from .exceptions import SberbankApiError


def clear_none(d: dict) -> dict:
    return {key: value for key, value in d.items() if value is not None}


class SberbankApi:
    base_url = "https://securepayments.sberbank.ru/payment/"

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def register_payment(
        self,
        *,
        order_num: str,
        amount: str,
        return_url: str,
        fail_url: str,
        description: Optional[str] = None,
        page_view: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> PaymentRedirect:
        r = requests.post(
            self.build_url("rest/register.do"),
            params=clear_none(
                {
                    "userName": self.username,
                    "password": self.password,
                    "orderNumber": order_num,
                    "amount": amount,
                    "returnUrl": return_url,
                    "failUrl": fail_url,
                    "description": description,
                    "pageView": page_view,
                    "phone": phone,
                }
            ),
        )
        if not r.ok:
            raise SberbankApiError(r)
        data = r.json()
        if data.get("errorCode"):
            raise SberbankApiError(r)
        return PaymentRedirect(data["formUrl"])

    def build_url(self, path: str) -> str:
        return urljoin(self.base_url, path)
