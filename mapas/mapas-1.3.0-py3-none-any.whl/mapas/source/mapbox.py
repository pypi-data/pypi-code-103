from .base import XYZSource


class Mapbox(XYZSource):
    def __init__(
            self, username: str, style_id: str, token: str, retries: int = 5):
        self.username = username
        self.style_id = style_id
        self.token = token

    def get_uri_for_resource(self, z: int, x: int, y: int):
        uri = "https://api.mapbox.com/styles/v1/{username}/{style_id}/tiles/256/{z}/{x}/{y}".format(
            username=self.username,
            style_id=self.style_id,
            z=z,
            x=x,
            y=y,
        )

        return uri

    def get_request_params(self, *args):
        return {
            'access_token': self.token,
        }

    def get_tile_size(self):
        return 256
