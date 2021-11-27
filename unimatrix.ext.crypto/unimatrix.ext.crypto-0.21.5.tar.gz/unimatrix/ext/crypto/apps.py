# pylint: disable=W0107
"""Declares :class:`ApplicationConfig`."""
import ioc.loader
from django.apps import AppConfig
from django.conf import settings


class ApplicationConfig(AppConfig):
    """Configures the :mod:`unimatrix.ext.crypto` package."""
    name = 'unimatrix.ext.crypto'
    label = 'crypto'

    def ready(self):
        """Invoked when the Django app registry has loaded all
        apps.
        """
        self.provider = ioc.loader.import_symbol(
            'unimatrix.ext.crypto.backends')
        for name, args in dict.items(getattr(settings, 'CRYPTO_BACKENDS', {})):
            backend_module = args.get('backend')
            params = args.get('options') or {}
            if backend_module is None:
                raise ValueError("The `backend` setting is required.")
            Backend = ioc.loader.import_symbol(f'{backend_module}.Backend')
            self.provider.add(name, Backend(params))
