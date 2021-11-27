"""Declares :class:`BaseResource`."""
from types import FunctionType
from types import LambdaType
from types import MethodType
from typing import Union


class BaseResource:

    @classmethod
    def as_list(cls, items: list):
        """Return a collection of the resource."""
        return cls.List(
            apiVersion=cls.List._version,
            kind=cls.List._kind,
            metadata={},
            items=items
        )

    @classmethod
    def as_resource(cls,
        spec: Union[dict, list],
        url: str = None,
        name: str = None,
        namespace: str = None
    ):
        """Create a fully-qualified representation of the resource."""
        metadata = {}
        if url is not None:
            metadata['self_link'] = url
        if namespace is not None:
            metadata['namespace'] = namespace
        if name is not None:
            metadata['name'] = name
        if isinstance(spec, dict):
            dto = cls(
                apiVersion=cls._version,
                kind=cls.__name__,
                metadata=metadata,
                spec=spec
            )
        elif isinstance(spec, list):
            raise NotImplementedError
        else:
            raise TypeError("Invalid type: " + type(spec))
        return dto
