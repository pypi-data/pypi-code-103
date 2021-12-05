"""Declares :class:`BaseResource`."""
from types import FunctionType
from typing import Union

from fastapi import Request
from fastapi.responses import Response
from fastapi.responses import JSONResponse

from ..resourceendpointset import ResourceEndpointSet


class BaseResource:

    @classmethod
    def as_list(cls, items: list, metadata: dict, reverse: FunctionType):
        """Return a collection of the resource."""
        return cls.List(
            apiVersion=cls.List._version,
            kind=cls.List._kind,
            metadata=metadata,
            items=[
                cls.as_resource(x, reverse(x))
                for x in items
            ]
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

    @classmethod
    def render_to_response(cls,
        endpoint: ResourceEndpointSet,
        request: Request,
        result: Union[list, dict],
        total_count: int = None
    ) -> Response:
        """Renders the result to a response.

        Args:
            endpoint (EndpointSet): the endpoint that is responding.
            request (fastapi.Request): the HTTP request to which a response
                is being served.
            result (dict, list): a dictionary (for a single object) or a list
                (for a result set).
            total_count (int): total items for this resource.

        Returns:
            :class:`BaseResource` or :class:`BaseResourceList`
        """
        metadata = {}
        if isinstance(result, list):
            metadata.update({
                'nextUrl': endpoint.get_next_url(total=total_count),
                'prevUrl': endpoint.get_prev_url()
            })
            if total_count is not None:
                metadata['totalItems'] = total_count
            response = cls.as_list(result, metadata, endpoint.get_detail_url)
        elif isinstance(result, dict):
            response = cls.as_resource(
                result, endpoint.get_detail_url(result)
            )
        else:
            raise TypeError(f"Invalid type: {result.__class__.__name__}")
        return response
