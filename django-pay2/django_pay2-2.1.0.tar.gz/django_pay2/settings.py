from django.conf import settings
from django.test.signals import setting_changed
from django.urls import reverse_lazy
from django.utils.module_loading import import_string

DEFAULTS = {
    # todo: сделать опцию, которая будет импортировать подключаемые платежные системы,
    # что позволит сделать подключаемые платежные системы, которые будут удобнее в отладке
    "ENABLED_PAYMENT_SYSTEMS": [
        "coinpayments",
        "free_kassa",
        "payeer",
        "perfect_money",
        "qiwi",
        "qiwi_kassa",
        "sberbank",
        "tinkoff",
    ],
    "DEBUG_MODE": False,
    "TEMPLATES": {
        "success": "django_pay2/success_payment.html",
        "rejected": "django_pay2/rejected_payment.html",
    },
    "TINKOFF": {
        "terminal_key": None,
        "password": None,
        "email_company": None,
        "taxation": None,
        "return_url": reverse_lazy("django_pay2:success"),
        "fail_url": reverse_lazy("django_pay2:fail"),
    },
    "PAYEER": {
        "account": None,
        "api_id": None,
        "api_password": None,
        "shop_id": None,
        "secret_key": None,
    },
    "FREE_KASSA": {
        "merchant_id": None,
        "secret_word_1": None,
        "secret_word_2": None,
    },
    "PERFECT_MONEY": {
        "payee_usd_account": None,
        "payee_eur_account": None,
        "payee_name": None,
        "alternate_passphrase": None,
        "success_url": reverse_lazy("django_pay2:success"),
        "failed_url": reverse_lazy("django_pay2:fail"),
    },
    "COINPAYMENTS": {
        "public_key": None,
        "private_key": None,
        "ipn_secret": None,
        "success_url": reverse_lazy("django_pay2:success"),
        "cancel_url": reverse_lazy("django_pay2:fail"),
    },
    "QIWI": {
        "secret_key": None,
    },
    "QIWI_KASSA": {
        "secret_key": None,
        "site_id": None,
    },
    "SBERBANK": {
        "username": None,
        "password": None,
        "return_url": reverse_lazy("django_pay2:success"),
        "fail_url": reverse_lazy("django_pay2:fail"),
        "public_key": None,
    },
}

IMPORT_DICTS = []


class ObjDict(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"Invalid setting: {item}")


class ImportDict(ObjDict):
    def __getattr__(self, item):
        val = super().__getattr__(item)
        if isinstance(val, str):
            return import_string(val)
        elif isinstance(val, (list, tuple)):
            return [import_string(s) for s in val]
        else:
            raise ValueError(f"Setting must be a string or list: {item}")


class PaymentSettings:
    def __init__(self, user_settings=None, defaults=None, import_dicts=None):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS
        self.import_dicts = import_dicts or IMPORT_DICTS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "PAYMENTS", {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError(f'Invalid payment settings: "{attr}"')

        try:
            val = self.user_settings[attr]
        except KeyError:
            val = self.defaults[attr]

        if isinstance(val, dict):
            dict_class = ImportDict if attr in self.import_dicts else ObjDict
            default = dict_class(self.defaults[attr])
            default.update(dict_class(val))
            val = default

        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


payment_settings = PaymentSettings()


def reload_app_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "PAYMENTS":
        payment_settings.reload()


setting_changed.connect(reload_app_settings)
