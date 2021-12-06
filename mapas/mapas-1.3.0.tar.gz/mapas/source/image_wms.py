from typing import Tuple, Dict, List, Optional

from .base import ImageSource


class ImageWms(ImageSource):
    def __init__(
            self, server_url: str, layers: List[str], *, cql_filter: str = '',
            alpha=1.0, auth=None):
        self.server_url = server_url
        self.layers = layers
        self.cql_filter = cql_filter
        self.auth = auth

    def get_uri_for_resource(
            self, bbox: Tuple[float, float, float, float],
            dimensions: Tuple[int, int]) -> str:
        return self.server_url

    def get_request_params(
            self, bbox: Tuple[float, float, float, float],
            dimensions: Tuple[int, int]) -> Dict[str, str]:
        params = {
            'SERVICE': 'WMS',
            'VERSION': '1.1.1',
            'REQUEST': 'GetMap',
            'FORMAT': 'image/png',
            'TRANSPARENT': 'true',
            'LAYERS': ','.join(self.layers),
            'exceptions': 'application/vnd.ogc.se_inimage',
            'SRS': 'EPSG:3857',
            'STYLES': '',
            'WIDTH': dimensions[0],
            'HEIGHT': dimensions[1],
            'BBOX': ','.join(map(str, bbox)),
        }

        if self.cql_filter:
            params['CQL_FILTER'] = self.cql_filter

        return params

    def get_auth(self) -> Optional[Tuple[str, str]]:
        return self.auth
