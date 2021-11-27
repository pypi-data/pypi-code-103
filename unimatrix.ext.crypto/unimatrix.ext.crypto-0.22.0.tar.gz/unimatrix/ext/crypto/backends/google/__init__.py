# pylint: disable=line-too-long
"""Declares :class:`GoogleCloudKMSLoader`."""
try:
    from google.cloud import kms
    from google.cloud.kms import CryptoKeyVersion
    from google.cloud import secretmanager
    DEPENDENCIES_INSTALLED = True
except ImportError:
    DEPENDENCIES_INSTALLED = False

from unimatrix.ext import crypto
from unimatrix.ext.crypto import oid
from unimatrix.ext.crypto import algorithms
from unimatrix.ext.crypto.exceptions import MissingDependencies
from unimatrix.ext.crypto.keyloader import KeyLoader
from unimatrix.ext.crypto.pkcs import RSAPublicKey
from unimatrix.ext.crypto.ec import EllipticCurvePublicKey


if DEPENDENCIES_INSTALLED:
    GOOGLE_ALGORITHMS = CryptoKeyVersion.CryptoKeyVersionAlgorithm
    CRYPTO_ALGORITHMS = {
        GOOGLE_ALGORITHMS.EC_SIGN_P256_SHA256: algorithms.SECP256R1SHA256,
        GOOGLE_ALGORITHMS.EC_SIGN_SECP256K1_SHA256: algorithms.SECP256K1SHA256,
        GOOGLE_ALGORITHMS.RSA_SIGN_PKCS1_4096_SHA256: algorithms.RSAPKCS1v15SHA256,
    }


class GoogleCloudKMSLoader(KeyLoader):
    """A :class:`~unimatrix.ext.crypto.KeyLoader` implementation that queries
    the Google KMS API to retrieve the available keys. Keys may optionally be
    included (or excluded) by adding a predicate using the ``filter``
    parameter.
    """

    @property
    def key_client_sync(self):
        if not hasattr(self, '_key_client_sync'):
            self._key_client_sync = kms.KeyManagementServiceClient()
        return self._key_client_sync

    @property
    def key_client(self):
        if not hasattr(self, '_key_client'):
            self._key_client = kms.KeyManagementServiceAsyncClient()
        return self._key_client

    async def sign(self, key, digest, algorithm, *args, **kwargs):
        """Returns the signature of `digest`."""
        response = await self.key_client.asymmetric_sign(
            request={
                'name': key.qualname,
                'digest': {algorithm.name: digest}
            }
        )
        assert key.public.verify(response.signature, digest, # nosec
            algorithm=algorithm, *args, **kwargs)
        return response.signature

    def setup(self, opts):
        """Hook called during instance initialization."""
        if not DEPENDENCIES_INSTALLED:
            raise MissingDependencies([
                'google-cloud-kms',
                'google-cloud-secret-manager'
            ])
        if not opts.get('project') or not isinstance(opts.project, str):
            raise TypeError('The `project` option is required (string)')
        if not opts.get('location') or not isinstance(opts.location, str):
            raise TypeError('The `location` option is required (string)')
        if not opts.get('keyring') or not isinstance(opts.keyring, str):
            raise TypeError('The `keyring` option is required (string)')
        self.project = opts.project
        self.location = opts.location
        self.keyring = opts.keyring

    def is_asymmetric(self, algorithm) -> bool:
        if not isinstance(algorithm, (list, set)):
            algorithm = set([algorithm])
        return bool(set(algorithm) & set([
            self.algorithms.RSA_SIGN_PKCS1_4096_SHA256
        ]))

    def get_algorithms(self, dto):
        return [ CRYPTO_ALGORITHMS[dto.algorithm] ]

    def get_public_key(self, client, dto):
        result = client.get_public_key(
            request={'name': dto.name},
            timeout=self.default_timeout
        )
        return crypto.frompem(result.pem)

    def get_qualname(self, dto):
        return dto.name

    def get_version(self, dto):
        return int(dto.name[-1])

    def get_sync(self, name, version=None):
        c = self.key_client_sync
        path = c.crypto_key_path(
            project=self.project, key_ring=self.keyring,
            location=self.location, crypto_key=name
        )
        self.logger.debug("Retrieving Google key %s", path)
        params = {
            'parent': path,
            'filter': "state=ENABLED",
        }
        version = None
        for version in c.list_crypto_key_versions(params, timeout=self.default_timeout):
            pass
        if version is None:
            # No enabled version
            raise self.DoesNotExist(name)

        return self.key_factory(c, name, version)
