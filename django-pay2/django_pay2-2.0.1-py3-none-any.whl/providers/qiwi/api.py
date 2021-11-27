import hashlib
import hmac

import requests

from django_pay2.payment_methods import PaymentRedirect
from django_pay2.settings import payment_settings


class QiwiApi:
    def __init__(self, secret_key):
        self.secret_key = secret_key

    def generate_payment_method(self, amount, currency, expirate_at, bill_id):
        response = requests.put(
            f"https://api.qiwi.com/partner/bill/v1/bills/{bill_id}",
            json={
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": currency,
                },
                "expirationDateTime": expirate_at.strftime("%Y-%m-%dT%H:%M:%S+03:00"),
            },
            headers={"Authorization": f"Bearer {self.secret_key}"},
        )
        response.raise_for_status()
        return PaymentRedirect(response.json()["payUrl"])

    def create_hmac(self, amount, currency, bill_id, site_id, status):
        return hmac.new(
            self.secret_key.encode("utf-8"),
            f"{amount}|{currency}|{bill_id}|{site_id}|{status}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()


def get_api():
    return QiwiApi(payment_settings.QIWI.secret_key)
