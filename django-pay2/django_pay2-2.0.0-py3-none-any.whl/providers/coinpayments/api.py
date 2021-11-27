import hashlib
import hmac
from urllib.parse import urlencode

import requests
from django.urls import reverse_lazy

from django_pay2.exceptions import CreatePaymentError
from django_pay2.payment_methods import PaymentRedirect
from django_pay2.settings import payment_settings


class CoinPaymentsApi:
    url = "https://www.coinpayments.net/api.php"

    notify_url = reverse_lazy("django_pay2:coinpayments:notify")

    def __init__(self, public_key, private_key, ipn_secret, success_url, cancel_url):
        self.public_key = public_key
        self.private_key = private_key
        self.ipn_secret = ipn_secret
        self.success_url = success_url
        self.cancel_url = cancel_url

    def generate_payment_method(self, request, amount, currency, order_id, buyer_email):
        response = self.request(
            {
                "cmd": "create_transaction",
                "amount": str(amount),
                "currency1": currency,
                "currency2": currency,
                "buyer_email": buyer_email,
                "invoice": str(order_id),
                "ipn_url": request.build_absolute_uri(self.notify_url),
                "success_url": request.build_absolute_uri(self.success_url),
                "cancel_url": request.build_absolute_uri(self.cancel_url),
            }
        )
        return PaymentRedirect(response["checkout_url"])

    def calculate_ipn_hmac(self, encoded_body):
        return hmac.new(
            self.ipn_secret.encode("utf-8"),
            encoded_body.encode("utf-8"),
            hashlib.sha512,
        ).hexdigest()

    def request(self, data):
        data.setdefault("version", 1)
        data.setdefault("key", self.public_key)

        encoded_body = self._encode_body(data)
        headers = {
            "HMAC": self.create_hmac(encoded_body),
        }
        response = requests.post(self.url, data=data, headers=headers)
        response.raise_for_status()
        res_data = response.json()
        if res_data["error"] != "ok":
            raise CreatePaymentError(res_data["error"])
        return res_data["result"]

    def create_hmac(self, encoded_body):
        return hmac.new(
            bytes(self.private_key, "utf-8"),
            encoded_body.encode("utf-8"),
            hashlib.sha512,
        ).hexdigest()

    @staticmethod
    def _encode_body(body: dict) -> str:
        return urlencode(body)


def get_api():
    return CoinPaymentsApi(
        payment_settings.COINPAYMENTS.public_key,
        payment_settings.COINPAYMENTS.private_key,
        payment_settings.COINPAYMENTS.ipn_secret,
        payment_settings.COINPAYMENTS.success_url,
        payment_settings.COINPAYMENTS.cancel_url,
    )
