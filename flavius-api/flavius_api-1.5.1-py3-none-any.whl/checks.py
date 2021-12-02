from django.core import checks

from flavius_api.conf import conf


@checks.register
def check_settings(app_configs, **kwargs):
    errors = []

    if not isinstance(conf.FLAVIUS_ENDPOINT_DEV, str):
        errors.append(
            checks.Error(
                "FLAVIUS_ENDPOINT_DEV should be a str.", id="flavius_api.E001"
            )
        )

    return errors
