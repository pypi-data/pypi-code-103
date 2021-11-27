from django.apps import AppConfig


class DjangoPayConfig(AppConfig):
    name = "django_pay2"
    verbose_name = "Платежи"

    def ready(self) -> None:
        import django_pay2.providers.coinpayments  # noqa:
        import django_pay2.providers.free_kassa  # noqa:
        import django_pay2.providers.payeer  # noqa:
        import django_pay2.providers.perfect_money  # noqa:
        import django_pay2.providers.qiwi  # noqa:
        import django_pay2.providers.qiwi_kassa  # noqa:
        import django_pay2.providers.sberbank  # noqa:
        import django_pay2.providers.tinkoff  # noqa:
