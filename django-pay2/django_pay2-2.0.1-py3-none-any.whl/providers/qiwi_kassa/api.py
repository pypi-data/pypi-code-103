import hashlib
import hmac

import requests

from django_pay2.payment_methods import PaymentRedirect
from django_pay2.settings import payment_settings


class QiwiKassaApi:
    def __init__(self, secret_key, site_id):
        self.secret_key = secret_key
        self.site_id = site_id

    def generate_payment_method(self, amount, currency, expirate_at, bill_id):
        response = requests.put(
            f"https://api.qiwi.com/partner/payin/v1/sites/{self.site_id}/bills/{bill_id}",
            json={
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": currency,
                },
                "expirationDateTime": expirate_at.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                "flags": ["SALE"],
            },
            headers={"Authorization": f"Bearer {self.secret_key}"},
        )
        response.raise_for_status()
        return PaymentRedirect(response.json()["payUrl"])

    def create_hmac(self, payment_id, created_datetime, amount):
        return hmac.new(
            self.secret_key.encode("utf-8"),
            f"{payment_id}|{created_datetime}|{amount}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()


def get_api():
    return QiwiKassaApi(
        payment_settings.QIWI_KASSA.secret_key,
        payment_settings.QIWI_KASSA.site_id,
    )
