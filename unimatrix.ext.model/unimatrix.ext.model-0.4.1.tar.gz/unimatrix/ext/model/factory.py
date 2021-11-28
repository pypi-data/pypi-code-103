"""Declares :class:`Factory` and its interface."""
from typing import Union


DOMAIN_RETURNTYPES = Union[AggregrateRoot, ValueObject, Entity]

class IFactory:

    def fromdict(self, dto: dict) -> DOMAIN_RETURNTYPES:
        """Instantiate a domain object from a Python dictionary."""
        raise NotImplementedError

    def fromdao(self, dto: dict) -> DOMAIN_RETURNTYPES:
        """Instantiate a domain object from a Data Access Object (DAO) .e.g
        an ORM-mapped class instance.
        """
        raise NotImplementedError
