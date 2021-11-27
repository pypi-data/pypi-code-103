import hashlib

from django_pay2.payment_methods import PaymentForm
from django_pay2.settings import payment_settings
from django_pay2.utils import remove_trivial_zeros


class FreeKassaApi:
    form_url = "https://www.free-kassa.ru/merchant/cash.php"

    def __init__(self, merchant_id, secret_word_1, secret_word_2):
        self.merchant_id = merchant_id
        self.secret_word_1 = secret_word_1
        self.secret_word_2 = secret_word_2

    def generate_payment_method(self, amount, order_id):
        return PaymentForm(
            action=self.form_url,
            fields={
                "m": self.merchant_id,
                "oa": str(amount),
                "o": str(order_id),
                "s": self.generate_form_sign(amount, order_id),
            },
        )

    def generate_form_sign(self, amount, order_id):
        hash_str = f"{self.merchant_id}:{amount}:{self.secret_word_1}:{order_id}"
        return hashlib.md5(hash_str.encode("utf-8")).hexdigest()

    def generate_notify_sign(self, amount, order_id):
        hash_str = f"{self.merchant_id}:{remove_trivial_zeros(amount)}:{self.secret_word_2}:{order_id}"
        return hashlib.md5(hash_str.encode("utf-8")).hexdigest()


def get_api():
    return FreeKassaApi(
        payment_settings.FREE_KASSA.merchant_id,
        payment_settings.FREE_KASSA.secret_word_1,
        payment_settings.FREE_KASSA.secret_word_2,
    )
