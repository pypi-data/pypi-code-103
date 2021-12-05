import folium
import io
from PyQt5.QtWebEngineWidgets import QWebEngineView  # pip install PyQtWebEngine


class Map:
    def __init__(self, parent=None):
        self.web_view = QWebEngineView(parent)
        self.web_view.setMinimumSize(640, 480)
        self.map = None

    def init(self, lat, lon):
        self.map = folium.Map(
            tiles="Stamen Terrain",
            location=(lat, lon),
            zoom_start=3,
        )

    def add_pass(self, lat, lon, start_time, end_time, color):
        folium.PolyLine(
            locations=zip(lat, lon),
            weight=5,
            tooltip="{} - {}".format(start_time, end_time),
            color=color,
        ).add_to(self.map)

    def add_site(self, lat, lon, comment):
        folium.Marker((lat, lon), popup=comment).add_to(self.map)

    def render(self):
        data = io.BytesIO()
        self.map.save(data, close_file=False)
        self.web_view.setHtml(data.getvalue().decode())
