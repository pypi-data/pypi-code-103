# pylint: skip-file
import ioc
from unimatrix.conf import settings

from .conf import configure
from .secret import get_signer
from .secret import get_secret_key
from .defaultkeystore import DefaultKeystore
from .truststore import trust


def setup_ioc(*args, **kwargs):
    ioc.provide('ApplicationSigner', get_signer())
    ioc.provide('ApplicationSecretKey', get_secret_key())
    if not ioc.is_satisfied('CryptoKeyStore'):
        ioc.provide('CryptoKeyStore', DefaultKeystore())
    if not ioc.is_satisfied('TrustStore'):
        ioc.provide('TrustStore', trust)


async def on_setup():
    await configure(
        loaders=getattr(settings, 'CRYPTO_KEYLOADERS', [])
    )
