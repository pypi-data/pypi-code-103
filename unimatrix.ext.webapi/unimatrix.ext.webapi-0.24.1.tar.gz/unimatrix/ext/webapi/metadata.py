"""Declares :class:`APIMetadataService`."""
import re
from typing import List


class APIMetadataService:
    """Provides an interface to query the API metadata."""

    async def get(self, asgi, request):
        """Return a dictionary holding all API properties."""
        return {
            'version': 'v2',
            'capabilities': await self.capabilities(asgi, request),
            'catalog': await self.catalog(asgi, request),
            'client': {'ip': str(request.client.host)}
        }

    async def catalog(self, asgi, request) -> dict:
        """Construct the API catalog."""
        return {
            x.name: {
                'url': self._make_absolute_path(request, x)
            }
            for x in asgi.routes
        }

    async def capabilities(self, asgi, request) -> List[str]:
        """Return the list of API capabilities."""
        return []

    def _has_path_params(self, path):
        return bool(re.findall('\{(.*?)\}', path))

    def _make_absolute_path(self, request, route):
        if not self._has_path_params(route.path):
            return request.url_for(route.name)

        return str.rstrip(str(request.base_url), '/')\
            + '/'\
            + str.lstrip(route.path, '/')
