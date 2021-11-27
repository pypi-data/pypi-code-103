# pylint: disable=line-too-long
"""Declares :class:`AzureBackend`."""
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
try:
    from azure.identity import DefaultAzureCredential as SyncDefaultAzureCredential
    from azure.identity.aio import DefaultAzureCredential
    from azure.keyvault.keys.aio import KeyClient
    from azure.keyvault.keys import KeyClient as SyncKeyClient
    from azure.keyvault.keys.crypto.aio import CryptographyClient
    #from azure.keyvault.keys.crypto.aio import SignatureAlgorithm
    DEPENDENCIES_INSTALLED = True
except ImportError:
    DEPENDENCIES_INSTALLED = False
from .. import oid
from ..ec import EllipticCurvePublicKey
from ..pkcs import RSAPublicKey
from ..keyloader import KeyLoader


class AzureBackend(KeyLoader):
    public_key_classes = {
        'EC': EllipticCurvePublicKey,
        'RSA': RSAPublicKey
    }

    supported_algorithms = {
        oid.RSAPKCS1v15SHA256: 'RS256',
        oid.RSAPKCS1v15SHA384: 'RS384',
        oid.RSAPKCS1v15SHA512: 'RS512',
        oid.SECP256K1: 'ECDSA256',
    }

    @property
    def credential(self) -> DefaultAzureCredential:
        """Return a :class:`azure.identity.aio.DefaultAzureCredential`
        instance.
        """
        return DefaultAzureCredential()

    @property
    def credential_sync(self) -> SyncDefaultAzureCredential:
        """Return a :class:`azure.identity.DefaultAzureCredential`
        instance.
        """
        return SyncDefaultAzureCredential()

    @property
    def key_client(self) -> KeyClient:
        """Return a :class:`azure.identity.aio.KeyClient` instance."""
        return KeyClient(
            vault_url=self.vault_url,
            credential=self.credential
        )

    @property
    def key_client_sync(self) -> SyncKeyClient:
        """Return a :class:`azure.identity.KeyClient` instance."""
        return SyncKeyClient(
            vault_url=self.vault_url,
            credential=self.credential_sync
        )

    @property
    def vault_url(self) -> str:
        """Return a string containing the Azure Key Vault URL."""
        return f"https://{self.vault}.vault.azure.net/"

    def get_crypto_client(self, keyid) -> CryptographyClient:
        """Return a :class:`CryptographyClient` instance."""
        return CryptographyClient(keyid, self.credential)

    def setup(self, opts):
        """Hook called during instance initialization."""
        if not DEPENDENCIES_INSTALLED:
            raise MissingDependencies([
                'azure-identity',
                'azure-keyvault',
                'azure-keyvault-key',
            ])
        self.vault = opts.vault

    def get_sync(self, name):
        with self.key_client_sync as c:
            return self.key_factory(c, name, c.get_key(name))

    async def get(self, name):
        async with self.key_client as c:
            return self.key_factory(c, name, await c.get_key(name))

    async def list(self):
        async with self.key_client as client:
            async for ref in client.list_properties_of_keys():
                yield AzurePrivateKey.fromclient(
                    client, await client.get_key(ref.name))

    async def sign(self, key, digest, algorithm, oid, *args, **kwargs):
        async with self.get_crypto_client(key.qualname) as c:
            result = await c.sign(self.get_platform_algorithm_name(oid), digest)
        sig = result.signature

        # Elliptic curve signatures are returned by Azure as a byte-sequence
        # of the concatenated r, s, but the cryptography module expects a
        # DSS encoded signature.
        if self.supported_algorithms[oid] in ('ECDSA256',):
            assert len(result.signature) == 64 # nosec
            sig = encode_dss_signature(
                int.from_bytes(result.signature[:32], 'big'),
                int.from_bytes(result.signature[32:64], 'big'),
            )
        assert key.verify(sig, digest, algorithm=algorithm, **kwargs) # nosec
        return sig

    def get_public_key(self, client, dto) -> str:
        if not bool(set(['sign', 'verify']) & set(dto.key_operations)):
            return None
        cls = self.public_key_classes.get(dto.key.kty)
        if cls is None:
            raise NotImplementedError(dto.key.kty)
        return cls.fromjwk(dto.key)

    def get_qualname(self, dto):
        return dto.key.kid

    def get_version(self, dto):
        return dto.properties.version

    def get_algorithms(self, dto):
        capabilities = set()
        if dto.key.kty == 'RSA':
            if bool(set(['sign', 'verify']) & set(dto.key_operations)):
                capabilities |= set([
                    oid.RSAPKCS1v15SHA256,
                    oid.RSAPKCS1v15SHA384,
                    oid.RSAPKCS1v15SHA512,
                ])

            if bool(set(['encrypt', 'decrypt']) & set(dto.key_operations)):
                raise NotImplementedError

        if dto.key.kty == 'EC':
            if bool(set(['sign', 'verify']) & set(dto.key_operations)):
                capabilities |= set([
                    oid.SECP256K1
                ])
            else:
                raise NotImplementedError

        if not capabilities:
            raise NotImplementedError
        return capabilities
