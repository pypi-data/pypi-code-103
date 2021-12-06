from .renderer import Renderer


class Map:
    def __init__(
            self, width=600, height=400, center_lat=19.53770903356431,
            center_lon=-96.92456245422363, zoom=15, layers=None):
        self.layers = layers

        self.zoom = zoom

        self.center_lat = center_lat
        self.center_lon = center_lon

        self.width = width
        self.height = height

    def set_center(self, lon: float, lat: float):
        self.center_lon = lon
        self.center_lat = lat

    def set_zoom(self, zoom: int):
        self.zoom = zoom

    def render(self) -> Renderer:
        canvas = Renderer(self.width, self.height)

        for layer in self.layers:
            layer.render(
                canvas,
                (self.center_lon, self.center_lat),
                (self.width, self.height),
                self.zoom
            )

        return canvas

    def save(self, filename):
        self.render_to_image().save(filename)
