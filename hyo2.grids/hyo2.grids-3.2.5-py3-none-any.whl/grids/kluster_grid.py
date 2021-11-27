import os
import traceback
from typing import List, Optional
import logging

from osgeo import osr

try:
    from bathygrid.convenience import load_grid, BathyGrid
    supported_kluster_bathygrid = True
except ImportError:
    # traceback.print_exc()
    supported_kluster_bathygrid = False
    load_grid = None

logger = logging.getLogger(__name__)
logger.debug("Kluster's BathyGrid supported: %s" % supported_kluster_bathygrid)


class KlusterGrid:

    class GridBbox:

        def __init__(self):
            self.min_x = 0.0
            self.max_x = 0.0
            self.min_y = 0.0
            self.max_y = 0.0
            self.res_x = 0.0
            self.res_y = 0.0
            self.rows = 0
            self.cols = 0
            self.hrs = str()
            self.vrs = str()
            self.transform = list()

        def __repr__(self):
            msg = "GridBbox\n"
            msg += "\tx: min %.4f, max %.4f\n" % (self.min_x, self.max_x)
            msg += "\ty: min %.4f, max %.4f\n" % (self.min_y, self.max_y)
            msg += "\tres: x %.4f, y %.4f\n" % (self.res_x, self.res_y)
            msg += "\trows: %d, cols %d\n" % (self.rows, self.cols)
            msg += "\thrs: %s\n" % self.hrs
            msg += "\tvrs: %s\n" % self.vrs
            msg += "\ttransform: %s" % self.vrs
            return msg

    class GridTile:
        def __init__(self):
            self.bbox = None  # type: Optional[KlusterGrid.GridBbox]
            self.layers = dict()

        def str(self) -> str:
            return str(self)

        def type(self, layer_name: str):
            if layer_name not in self.layers.keys():
                raise RuntimeError("Missing layer: %s" % layer_name)
            tt = str(self.layers[layer_name].dtype)
            if tt == "float32":
                return "KLUSTER_FLOAT32"
            elif tt == "int32":
                return "KLUSTER_INTEGER32"
            raise RuntimeError("Unsupported layer type %s: %s" % (tt, layer_name))

        def band_index(self, layer_name: str):
            return layer_name

        def convert_easting(self, c: int):
            return self.bbox.transform[0] + (c + 0.5) * self.bbox.transform[1]

        def convert_northing(self, r: int):
            return self.bbox.transform[3] + (self.bbox.rows - r - 1.5) * self.bbox.transform[5]

        def __repr__(self):
            msg = "GridTile\n"
            msg += "\ttiles: %d" % len(self.layers)
            return msg

    def __init__(self):
        if not supported_kluster_bathygrid:
            raise RuntimeError("Unsupported Kluster Grids. First install the Bathygrid module")
        self._cb = None
        self._bg = None  # type: Optional[BathyGrid]
        self._path = None  # type: Optional[str]
        self._tiles = None  # type: Optional[List[GridTile]]
        self._bbox = None  # type: Optional[KlusterGrid.GridBbox]

        self._first_tile = True
        self._res_idx = 0

    def set_progress_callback(self, cb):
        self._cb = cb

    def open_to_read(self, path: str, chunk_size: Optional[int] = None):
        self._bg = load_grid(folder_path=path)
        self._path = path
        self._bbox = self.GridBbox()
        self._bbox.min_x = self._bg.min_x
        self._bbox.min_y = self._bg.min_y
        self._bbox.max_x = self._bg.max_x
        self._bbox.max_y = self._bg.max_y
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(self._bg.epsg)
        self._bbox.hrs = srs.ExportToWkt()
        self._bbox.vrs = self._bg.vertical_reference

    def read_band_names(self) -> List[str]:
        return self._bg.layer_names

    def bbox(self) -> GridBbox:
        return self._bbox

    def is_bag(self) -> bool:
        return False

    def is_csar(self) -> bool:
        return False

    def is_vr(self) -> bool:
        sub_folders = os.listdir(self._path)
        for sf in sub_folders:
            if sf == 'VRGridTile_Root':
                return True
        return False

    def read_next_tile(self, layers: List[str]):
        if self._first_tile:
            self._res_idx = 0
            self._first_tile = False

        self._tiles = list()

        if self._res_idx >= len(self._bg.resolutions):
            return False

        res = self._bg.resolutions[self._res_idx]
        logger.debug('reading resolution %s' % res)
        gt = KlusterGrid.GridTile()
        gt.bbox = self.bbox()
        gt.bbox.transform = self._bg.get_geotransform(resolution=res)
        gt.bbox.res_x = res
        gt.bbox.res_y = res
        for layer in layers:
            gt.layers[layer] = self._bg.get_layers_by_name(layer=layer, resolution=res)[0]
            gt.bbox.rows = gt.layers[layer].shape[0]
            gt.bbox.cols = gt.layers[layer].shape[1]
            # logger.debug(gt.layers[layer])
        self._tiles.append(gt)
        self._res_idx += 1

        return True

    @property
    def tiles(self) -> Optional[List[GridTile]]:
        return self._tiles

    def clear(self):
        self._bg = None
        self._path = None
        self._tiles = None
        self._bbox = None

        self._first_tile = True
        self._res_idx = 0

    def __repr__(self):
        msg = "KlusterGrid\n"
        msg += "\tpath: %s" % self._path
        return msg
