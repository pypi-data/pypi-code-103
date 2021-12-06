from mapas import Tile

from .testutils import FakeSource, FakeRenderer


def test_downloads_the_correct_range_of_tiles():
    source = FakeSource()
    layer = Tile(source=source)
    canvas = FakeRenderer()

    layer.render(canvas, (-96.92157983779907, 19.518436152371653), (600, 400), 17)

    assert source.tile_requests[0]['args'] == (17, 30246, 58287)
    assert source.tile_requests[1]['args'] == (17, 30246, 58288)
    assert source.tile_requests[2]['args'] == (17, 30247, 58287)
    assert source.tile_requests[3]['args'] == (17, 30247, 58288)
    assert source.tile_requests[4]['args'] == (17, 30248, 58287)
    assert source.tile_requests[5]['args'] == (17, 30248, 58288)
    assert source.tile_requests[6]['args'] == (17, 30249, 58287)
    assert source.tile_requests[7]['args'] == (17, 30249, 58288)

    assert canvas.calls[0]['args'][1] == (-194, -50)
    assert canvas.calls[1]['args'][1] == (-194, 206)
    assert canvas.calls[2]['args'][1] == (62, -50)
    assert canvas.calls[3]['args'][1] == (62, 206)
    assert canvas.calls[4]['args'][1] == (318, -50)
    assert canvas.calls[5]['args'][1] == (318, 206)
    assert canvas.calls[6]['args'][1] == (574, -50)
    assert canvas.calls[7]['args'][1] == (574, 206)
