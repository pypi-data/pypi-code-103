from PIL import Image

from mapas import Map, Tile
from mapas.renderer import Renderer

from .testutils import FakeSource


def test_the_expected_api():
    source = FakeSource()
    mapa = Map(
        width=600,
        height=400,
        layers=[
            Tile(source=source),
        ],
    )

    mapa.set_center(-96.92157983779907, 19.518436152371653)
    mapa.set_zoom(17)

    renderer = mapa.render()

    assert isinstance(renderer, Renderer)

    img = renderer.get_png_bytes()

    Image.open(img)
