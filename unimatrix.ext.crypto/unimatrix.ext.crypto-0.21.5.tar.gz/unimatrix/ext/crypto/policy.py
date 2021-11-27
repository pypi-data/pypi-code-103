"""Declares classes and functions to enforce key trust
policies.
"""
import functools
import operator

from unimatrix.ext.crypto.trustedpublickey import TrustedPublicKey


class Policy:

    def is_satisfied(self, key: TrustedPublicKey) -> bool:
        """Return a boolean indicating if the policy is
        satisfied by the key.
        """
        raise NotImplementedError

    def __and__(x, y):
        return x.is_satisfied(y)\
            if isinstance(y, TrustedPublicKey)\
            else And(x, y)

    def __or__(x, y):
        return x.is_satisfied(y)\
            if isinstance(y, TrustedPublicKey)\
            else Or(x, y)

    def __xor__(x, y):
        if not isinstance(y, TrustedPublicKey):
            raise TypeError(
                "The right-hand side of the | operator must be Policy"
            )
        return not x.is_satisfied(y)

    def __invert__(self):
        return Negate(self)


class And(Policy):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_satisfied(self, key: TrustedPublicKey) -> bool:
        return self.x.is_satisfied(key) and self.y.is_satisfied(key)


class Negate(Policy):

    def __init__(self, policy):
        self.policy = policy

    def is_satisfied(self, key: TrustedPublicKey) -> bool:
        return not self.policy.is_satisfied(key)


class Or(Policy):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_satisfied(self, key: TrustedPublicKey) -> bool:
        return self.x.is_satisfied(key) or self.y.is_satisfied(key)


class IsTagged(Policy):

    def __init__(self, tag: str, tags: list = None):
        self.value = tag
        self.tags = tags or []

    def is_satisfied(self, key: TrustedPublicKey) -> bool:
        if self.tags and not any(map(key.is_tagged, self.tags)):
            return True
        return key.is_tagged(self.value)


class HasAnnotation(Policy):

    def __init__(self, annotation):
        self.annotation = annotation

    def is_satisfied(self, key: TrustedPublicKey) -> bool:
        return key.is_annotated(self.annotation)


def combine(*policies):
    """Syntax simplification to AND multiple policies."""
    return functools.reduce(operator.and_, policies)
