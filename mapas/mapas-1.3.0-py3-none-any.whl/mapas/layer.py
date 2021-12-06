from typing import Tuple

from .renderer import Renderer
from .tiles import (
    tiles_to_cover, topleft_tile, topleft_coords, get_tile_offset,
    lon_lat_to_web_merkator, compute_real_world_m_per_px,
)
from .vector import add, sub, div, mul


class Layer:
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha


class Tile(Layer):
    def __init__(self, source, *, alpha: float = 1.0):
        super().__init__(alpha=alpha)
        self.source = source

    def render(
            self, canvas: Renderer, center: Tuple[float, float],
            dimensions: Tuple[int, int], zoom: int):
        ''' Renders this tiles onto the surface, retrieving them from the
        source.'''
        tile_size = self.source.get_tile_size()
        center_tile_offset = get_tile_offset(tile_size, zoom, center)
        x_tiles, y_tiles = tiles_to_cover(
            dimensions,
            tile_size,
            center_tile_offset,
        )
        tl_tile = topleft_tile(dimensions, tile_size, zoom, center, center_tile_offset)
        tl_coords = topleft_coords(dimensions, tile_size, center_tile_offset)

        for i in range(x_tiles):
            for j in range(y_tiles):
                tile = self.source.get_tile_png(zoom, tl_tile[0] + i, tl_tile[1] + j)

                canvas.paste(tile, (
                    int(tl_coords[0]) + i * tile_size,
                    int(tl_coords[1]) + j * tile_size
                ), alpha=self.alpha)


class Image(Layer):
    def __init__(self, source, *, alpha: float = 1.0):
        super().__init__(alpha=alpha)
        self.source = source

    def render(
            self, canvas: Renderer, center: Tuple[float, float],
            dimensions: Tuple[int, int], zoom: int):
        ''' Renders this image source onto the surface '''
        center_3857 = lon_lat_to_web_merkator(*center)
        real_world_m_per_px = compute_real_world_m_per_px(center[1], zoom)
        corner_1 = add(center_3857, mul(div(dimensions, 2), real_world_m_per_px))
        corner_2 = sub(center_3857, mul(div(dimensions, 2), real_world_m_per_px))
        bbox_epsg_3857 = [
            min(corner_1[0], corner_2[0]),
            min(corner_1[1], corner_2[1]),
            max(corner_1[0], corner_2[0]),
            max(corner_1[1], corner_2[1]),
        ]

        tile = self.source.get_image_png(bbox_epsg_3857, dimensions)

        canvas.alpha_composite(tile, alpha=self.alpha)
