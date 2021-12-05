"""Declares :class:`KeyTrustPolicy`."""
import functools
import operator

from unimatrix.ext.crypto import policy
from unimatrix.ext.crypto.trustedpublickey import TrustedPublicKey

from .exceptions import TrustIssues


class KeyTrustPolicy:
    """Declares a policy to determine if a certain public key is trusted."""

    def __init__(self, tags: list, **annotations):
        if annotations:
            raise NotImplementedError
        if len(tags) == 0: # pragma: no cover
            raise ValueError("Specicy at least one tag.")
        self.operator = functools.reduce(
            operator.and_, map(policy.IsTagged, tags)
        )

    async def enforce(self, key: TrustedPublicKey):
        """Enforces the policy against the given key."""
        if not (self.operator & key):
            raise TrustIssues
