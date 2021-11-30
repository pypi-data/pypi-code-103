from contextlib import suppress

from typing import Any, List

try:
    from ujson import dumps

except ImportError:
    from json import dumps  # type: ignore[misc]

__all__ = [

]

with suppress(ImportError):
    from aiohttp.web import Request, Response, json_response  # noqa
    from multidict import MultiDictProxy  # noqa


    class AiohttpRESTViewMixin:
        """
        Aiohttp framework REST view mixin.
        """
        @property
        def _current_route_parts(self) -> List[str]:
            request: Request = self.request  # type: ignore[attr-defined]
            return request.path.strip('/').split('/')

        @property
        def _get_params(self) -> MultiDictProxy[str]:
            request: Request = self.request  # type: ignore[attr-defined]
            return request.query

        def _get_params_getall(self, param: str) -> List[str]:
            try:
                return self._get_params.getall(param)
            except KeyError:
                return []

        @staticmethod
        def _render(
            data: Any,
        ) -> Response:
            """Rendering valid answer."""
            if isinstance(data, str):
                return Response(text=data)

            return json_response(data, dumps=dumps)

    __all__.append(AiohttpRESTViewMixin.__name__)
