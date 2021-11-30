from contextlib import suppress

from typing import Any, List

__all__ = [

]

with suppress(ImportError):
    from pyramid.request import Request  # noqa
    from pyramid.response import Response  # noqa
    from webob.multidict import GetDict  # noqa

    class PyramidRESTViewMixin:
        """
        Pyramid framework REST view mixin.
        """
        @property
        def _current_route_parts(self) -> List[str]:
            request: Request = self.request  # type: ignore[attr-defined]
            return request.path.strip('/').split('/')

        def _add_error(
            self,
            msg: Any,
            *args,  # pylint: disable=unused-argument  # noqa
            name: str = 'error',
            **kwargs,  # pylint: disable=unused-argument  # noqa
        ) -> None:  # noqa
            request: Request = self.request  # type: ignore[attr-defined]
            request.errors.add(
                request.current_route_path(),
                name,
                msg,
            )

        def _render_error(
            self,
            *args,  # pylint: disable=unused-argument  # noqa
            **kwargs,  # pylint: disable=unused-argument  # noqa
        ) -> Response:
            request: Request = self.request  # type: ignore[attr-defined]
            return Response(
                status=400,
                json={
                    "status": "error",
                    "errors": request.errors,
                },
            )

        @property
        def _get_params(self) -> GetDict:
            request: Request = self.request  # type: ignore[attr-defined]
            return request.GET

        def _get_params_getall(self, param: str) -> List[str]:
            return self._get_params.getall(param)

        @staticmethod
        def _render(
            data: Any,
        ) -> Response:
            """Rendering valid answer."""
            if isinstance(data, str):
                return Response(text=data)

            return Response(json=data)


    __all__.append(PyramidRESTViewMixin.__name__)
