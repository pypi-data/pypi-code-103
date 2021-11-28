import hashlib

from django.urls import reverse_lazy

from django_pay2.payment_methods import PaymentForm
from django_pay2.settings import payment_settings


class PerfectMoneyApi:
    form_url = "https://perfectmoney.is/api/step1.asp"

    notify_url = reverse_lazy("django_pay2:perfect_money:notify")

    def __init__(
        self,
        payee_usd_account,
        payee_eur_account,
        payee_name,
        success_url,
        failed_url,
        alternate_passphrase,
    ):
        self.payee_usd_account = payee_usd_account
        self.payee_eur_account = payee_eur_account
        self.payee_name = payee_name
        self.success_url = success_url
        self.failed_url = failed_url
        self.alternate_passphrase = alternate_passphrase

    def generate_payment_method(self, request, amount, currency, order_id):
        return PaymentForm(
            action=self.form_url,
            fields={
                "PAYEE_ACCOUNT": self.get_payee(currency),
                "PAYEE_NAME": self.payee_name,
                "PAYMENT_AMOUNT": f"{amount:.2f}",
                "PAYMENT_UNITS": currency,
                "PAYMENT_ID": str(order_id),
                "STATUS_URL": request.build_absolute_uri(self.notify_url),
                "PAYMENT_URL": request.build_absolute_uri(self.success_url),
                "NOPAYMENT_URL": request.build_absolute_uri(self.failed_url),
                "BAGGAGE_FIELDS": "",
            },
        )

    def calculate_sign(
        self,
        payment_id,
        payment_amount,
        payment_units,
        payment_batch_num,
        payer_account,
        timestamp,
    ):
        hashed_pass = (
            hashlib.md5(self.alternate_passphrase.encode("utf-8")).hexdigest().upper()
        )
        hash_list = [
            payment_id,
            self.get_payee(payment_units),
            payment_amount,
            payment_units,
            payment_batch_num,
            payer_account,
            hashed_pass,
            timestamp,
        ]
        sign = hashlib.md5(":".join([str(item) for item in hash_list]).encode("utf-8"))
        return sign.hexdigest().upper()

    def get_payee(self, currency):
        return self.payee_usd_account if currency == "USD" else self.payee_eur_account


def get_api():
    return PerfectMoneyApi(
        payment_settings.PERFECT_MONEY.payee_usd_account,
        payment_settings.PERFECT_MONEY.payee_eur_account,
        payment_settings.PERFECT_MONEY.payee_name,
        payment_settings.PERFECT_MONEY.success_url,
        payment_settings.PERFECT_MONEY.failed_url,
        payment_settings.PERFECT_MONEY.alternate_passphrase,
    )
