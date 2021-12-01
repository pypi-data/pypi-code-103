import logging
from typing import Any, Dict, Tuple

from django.urls import NoReverseMatch
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


__all__ = ["APIRootView"]


logger = logging.getLogger(__name__)


class APIRootView(APIView):
    """Welcome! This is the API root."""

    api_root_dict: Dict[str, Tuple[str, dict[str, Any]]] = {}

    authentication_classes = []
    permission_classes = []

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        routes = {}
        namespace = request.resolver_match.namespace
        for key, (url_name, params) in self.api_root_dict.items() or {}:
            if namespace:
                url_name = namespace + ":" + url_name
            params.update(kwargs)
            try:
                routes[key] = reverse(
                    viewname=url_name,
                    args=args,
                    kwargs=params,
                    request=request,
                    format=kwargs.get("format", None),
                )
            except NoReverseMatch:
                logger.info(f"No reverse found for {url_name} with kwargs {params}.")
                continue

        return Response(routes)
