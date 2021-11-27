import os
import traceback
from typing import Optional
import math
import logging

from hyo2.grids._grids import Grids, StringVec, grid_data_type
from hyo2.grids.kluster_grid import KlusterGrid, supported_kluster_bathygrid
from hyo2.grids.common.gdal_aux import GdalAux

from osgeo import osr

logger = logging.getLogger(__name__)

layer_types = {
    "depth": 0,
    "product_uncertainty": 1,
    "density": 2,
    "tvu_qc": 3,
}


class GridsManager:

    def __init__(self):

        # logger.debug("NEW GRID MANAGER")

        self._grid_list = list()
        self._cur_grids = None
        self._cur_path = None
        self._cur_basename = None
        self._tvu_qc_name = None
        self._select_layers = list()
        self._cb = None
        
    @classmethod
    def kluster_grid_supported(cls) -> bool:
        return supported_kluster_bathygrid

    @classmethod
    def grid_data_type(cls, type_id):
        return grid_data_type(type_id)

    @property
    def grid_list(self):
        return self._grid_list

    @property
    def cur_grids(self):
        return self._cur_grids

    @property
    def has_cur_grids(self):
        return self._cur_grids is not None

    @property
    def has_bag(self):
        for path in self.grid_list:
            if self.is_bag_path(path):
                return True

        return False

    @property
    def has_csar(self):
        for path in self.grid_list:
            if self.is_csar_path(path):
                return True

        return False

    @property
    def has_kluster(self):
        for path in self.grid_list:
            if self.is_kluster_path(path):
                return True

        return False

    @property
    def current_path(self):
        if not self._cur_path:
            raise RuntimeError('first make current a grid')

        return self._cur_path

    @property
    def current_basename(self):
        if not self._cur_basename:
            raise RuntimeError('first make current a grid')

        return self._cur_basename

    @property
    def tiles(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        return list(self._cur_grids.tiles)

    def clear_tiles(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        self._cur_grids.tiles.clear()

    def is_vr(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        return self._cur_grids.is_vr()

    def is_bag(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        return self._cur_grids.is_bag()

    def is_csar(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        return self._cur_grids.is_csar()

    def is_kluster_grid(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        return isinstance(self._cur_grids, KlusterGrid)

    def designated(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        self._cur_grids.populate_designated_soundings()

        return self._cur_grids.designated

    @property
    def selected_layers_in_current(self):
        
        return self._select_layers

    @selected_layers_in_current.setter
    def selected_layers_in_current(self, layers):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        if not isinstance(layers, list):
            raise RuntimeError('the function takes a list, but %s was passed' % type(layers))

        self._select_layers = layers

    @property
    def callback(self):
        return self._cb

    @callback.setter
    def callback(self, cb):
        # for line in traceback.format_stack():
        #     logger.debug("- %s" % line.strip())
        # logger.info("setting cb: %s" % cb)
        self._cb = cb

    # ### Manage file list ###

    @classmethod
    def is_bag_path(cls, path: str) -> bool:
        return os.path.splitext(path)[-1] == ".bag"

    @classmethod
    def is_csar_path(cls, path: str) -> bool:
        return os.path.splitext(path)[-1] == ".csar"

    @classmethod
    def is_kluster_path(cls, path: str) -> bool:
        if not os.path.exists(path):
            return False

        if not os.path.isdir(path):
            return False

        sub_folders = os.listdir(path)
        if len(sub_folders) == 0:
            logger.debug('Found no root folders in %s, expected a root folder like "VRGridTile_Root"' % path)
            return False

        valid_sub_folders = [fldr for fldr in sub_folders if fldr in ['VRGridTile_Root', 'SRGrid_Root']]
        if len(valid_sub_folders) > 1:
            logger.debug('Found multiple sub-folders in %s, expected one root folder like "VRGridTile_Root"' % path)
            return False

        if len(valid_sub_folders) == 0:
            logger.debug('Found no root folders in %s, expected a root folder like "VRGridTile_Root"' % path)
            return False

        return True

    def add_path(self, path):

        if not os.path.exists(path):
            raise RuntimeError("The passed file does not exist: %s" % path)

        if not isinstance(path, str) and not isinstance(path, str):
            raise RuntimeError("invalid object passed as file path: %s" % type(path))

        # check if supported format
        if not self.is_bag_path(path) and not self.is_csar_path(path) and not self.is_kluster_path(path):
            logger.warning('skipping unknown grid file extension for %s' % path)
            return

        # avoid file path duplications
        if path in self._grid_list:
            logger.warning('the file already present: %s' % path)
            return

        self._grid_list.append(path)

    def remove_path(self, path):
        # case that the grid file is not in the list
        if path not in self._grid_list:
            logger.warning('the file is not present: %s' % path)
            return

        self._grid_list.remove(path)

    def clear_grid_list(self):
        self._grid_list = list()

    # ### Actual data reading ###

    def set_current(self, path):
        # ### PRE-CHECKS ###

        # check that we got a string
        if not isinstance(path, str):
            raise RuntimeError("invalid object passed as file path: %s" % type(path))

        # check to avoid to load unlisted grids
        if path not in self._grid_list:
            logger.warning('the passed file is not in the current list: %s' % path)

        # check if the file still exist
        if not os.path.exists(path):
            raise RuntimeError('the passed path does not exist: %s' % path)

        self._cur_path = path
        self._cur_basename = os.path.splitext(os.path.basename(path))[0]
        # logger.debug("current path: %s" % self._cur_path)

        # clean all the previous allocated memory
        self._cur_grids = None

    def open_to_read_current(self, chunk_size):
        if self._cur_grids is not None:
            raise RuntimeError('first close current file')

        logger.debug("preparing %s" % self._cur_path)

        try:
            if self.is_kluster_path(self._cur_path):
                self._cur_grids = KlusterGrid()
            else:
                self._cur_grids = Grids(os.path.dirname(__file__))
            if self._cb:
                self._cur_grids.set_progress_callback(self._cb)
            self._cur_grids.open_to_read(self._cur_path, chunk_size)

        except Exception as e:
            self._cur_grids = None
            raise e

    def close_current(self):
        if self._cur_grids is None:
            raise RuntimeError('first make current a new file')

        try:
            self._cur_grids.clear()

        except Exception as e:
            self._cur_grids = None
            raise e

    def layer_names(self):
        if self._cur_grids is None:
            raise RuntimeError('first make current a new file')

        return self._cur_grids.read_band_names()

    def current_has_depth_layer(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        bands = self.layer_names()
        for bnd in bands:
            if self.is_csar():
                if bnd == "Depth":
                    return True
                if bnd == "Elevation":
                    return True
            elif self.is_bag():
                if self.is_vr():
                    if bnd == "VarRes_Elevation":
                        return True
                else:
                    if bnd == "Elevation":
                        return True
            elif self.is_kluster_grid():
                if bnd == "depth":
                    return True
        return False

    def depth_layer_name(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        if self.is_csar():
            bands = self.layer_names()
            for bnd in bands:
                if bnd == "Depth":
                    return "Depth"
                if bnd == "Elevation":
                    return "Elevation"
            raise RuntimeError("unsupported format")

        elif self.is_bag():
            if self.is_vr():
                return "VarRes_Elevation"
            else:
                return "Elevation"

        elif self.is_kluster_grid():
            return "depth"

        else:
            raise RuntimeError("unsupported format")

    def current_has_product_uncertainty_layer(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        bands = self.layer_names()
        for bnd in bands:
            if self.is_csar():
                if bnd == "Uncertainty":
                    return True
            elif self.is_bag():
                # try:
                #     if "productUncert" not in self._cur_grids.bbox().iso_metadata:
                #         return False
                # except Exception:
                #     pass

                if self.is_vr():
                    if bnd == "VarRes_Uncertainty":
                        return True
                else:
                    if bnd == "Uncertainty":
                        return True
            elif self.is_kluster_grid():
                if bnd == "vertical_uncertainty":
                    return True
        return False

    def product_uncertainty_layer_name(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        if self.is_csar():
            return "Uncertainty"
        elif self.is_bag():
            if self.is_vr():
                return "VarRes_Uncertainty"
            else:
                return "Uncertainty"
        elif self.is_kluster_grid():
            return "vertical_uncertainty"
        else:
            raise RuntimeError("unsupported format")

    def current_has_density_layer(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        bands = self.layer_names()
        for bnd in bands:
            if self.is_csar():
                if bnd == "Density":
                    return True
            elif self.is_bag():
                if self.is_vr():
                    if bnd == "VarRes_Density":
                        return True
                else:
                    if bnd == "Density":
                        return True
            elif self.is_kluster_grid():
                if bnd == "density":
                    return True
        return False
    
    def density_layer_name(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        if self.is_csar():
            return "Density"
        elif self.is_bag():
            if self.is_vr():
                return "VarRes_Density"
            else:
                return "Density"
        elif self.is_kluster_grid():
            return "density"
        else:
            raise RuntimeError("unsupported format")

    def current_tvu_qc_layers(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        # if not self.prepared_to_read:
        #     raise RuntimeError("first prepare to read!")

        bands = self.layer_names()
        layers = list()
        for bnd in bands:

            if self.is_csar():
                if bnd.lower().find('iho') >= 0 or bnd.lower().find('tvu qc') >= 0 or bnd.lower().find('tvu_qc') >= 0:
                    layers.append(bnd)
            elif self.is_bag():
                # BAG files do not have this kind of layers
                pass

        return layers

    def set_current_tvu_qc_name(self, name):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        self._tvu_qc_name = name

    def tvu_qc_layer_name(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        if self.is_csar():
            if self._tvu_qc_name is None:
                raise RuntimeError('the TVU QC name is not set')
            return self._tvu_qc_name
        # elif self.has_bag:
        #     # TODO
        #     pass
        else:
            raise RuntimeError("unsupported format")

    def pct_cc_layer_name(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        if self.is_csar():
            return "pct_cc"
        elif self.is_bag():
            return "pct_cc"
        else:
            raise RuntimeError("unsupported format")

    def pct_od_layer_name(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        if self.is_csar():
            return "pct_od"
        elif self.is_bag():
            return "pct_od"
        else:
            raise RuntimeError("unsupported format")

    def read_next_tile(self, layers):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')

        # logger.debug("reading layers: %s" % (layers, ))
        if self.is_kluster_grid():
            return self._cur_grids.read_next_tile(layers)
        else:
            return self._cur_grids.read_next_tile(StringVec(layers))

    @property
    def current_shape(self):
        if not self._cur_grids:
            raise RuntimeError('first make current a grid')
        return self._cur_grids.shape()

    # truncation

    def truncate(self, input_file, output_file, decimal_places=1):
        logger.debug("truncation with decimal places: %d" % decimal_places)
        grids = Grids(os.path.dirname(__file__))
        if self._cb:
            grids.set_progress_callback(self._cb)
        return grids.truncate(input_file, output_file, decimal_places)

    # xyz

    def xyz(self, input_file: str, output_file: str, geographic: bool,
            elevation: bool = False, truncate: bool = False, decimal_places: bool = False,
            epsg_code: Optional[int] = None, order: str = 'yxz'):

        logger.debug("input bag: %s" % input_file)
        logger.debug("output xyz: %s" % output_file)

        # check for invalid combination of geographic=True and passed epsg_code
        if isinstance(epsg_code, int) and (geographic is True):
            raise RuntimeError("invalid combination of parameters: geographic %s and epsg_code %s"
                               % (geographic, epsg_code))

        # if geographic, set the corresponding epsg code
        if geographic:
            epsg_code = 4326

        # check for invalid passed paramter
        if not isinstance(epsg_code, int) and (epsg_code is not None):
            raise RuntimeError("the passed epsg_code is not an integer: %s [%s]"
                               % (epsg_code, type(epsg_code)))
        logger.debug("EPSG code: %s" % epsg_code)

        # check validity for passed order
        if order not in ['xyz', 'xzy', 'yxz', 'yzx', 'zxy', 'zyx']:
            raise RuntimeError("unknown order: %s" % order)
        logger.debug("order: %s" % order)

        # instantiate Grids class
        grids = Grids(os.path.dirname(__file__))
        if self._cb:
            grids.set_progress_callback(self._cb)

        # actually reading the data from the file
        ret = grids.populate_xyz(input_file)
        if not ret:
            return False

        # retrieving the Z coordinates (and swapping the sign if required)
        zs = list(grids.xyz_zs)
        if not elevation:
            zs = [-z for z in zs]

        # applying (or not) the geographic conversion
        hrs = grids.xyz_hrs
        pts_size = len(grids.xyz_xs)
        quantum_size = int(pts_size / 100)
        if epsg_code is not None:
            logger.debug("converting to EPSG code: %d" % epsg_code)

            # creating GDAL coords transformer
            GdalAux.check_gdal_data()
            try:
                osr_csar = osr.SpatialReference()
                osr_csar.ImportFromWkt(hrs)
                osr_geo = osr.SpatialReference()
                osr_geo.ImportFromEPSG(epsg_code)  # EPSG code
                loc2geo = osr.CoordinateTransformation(osr_csar, osr_geo)

            except Exception as e:
                raise IOError("unable to create a valid coords transform: %s" % e)

            # actually doing the conversion
            xs = list()
            ys = list()
            for i, _ in enumerate(grids.xyz_xs):
                if (i % quantum_size) == 0:
                    logger.debug("transforming: %s/%s (%.1f%%)" % (i, pts_size, i/pts_size*100.0))
                    if self._cb:
                        self._cb.step_update("Transforming points", i, pts_size)
                x, y, _ = loc2geo.TransformPoint(grids.xyz_xs[i], grids.xyz_ys[i])
                xs.append(x)
                ys.append(y)

        else:  # no conversion required
            xs = grids.xyz_xs
            ys = grids.xyz_ys

        # writing to output text file
        logger.debug("points: %d" % len(xs))
        logger.debug("wkt: %s" % hrs)
        multi = 10.0**decimal_places
        with open(output_file, "w") as fod:
            for i, _ in enumerate(xs):

                if (i % quantum_size) == 0:
                    logger.debug("writing: %s/%s (%.1f%%)" % (i, pts_size, i / pts_size * 100.0))
                    if self._cb:
                        self._cb.step_update("Writing points", i, pts_size)

                if order == 'xyz':
                    if truncate:
                        fod.write(f"{xs[i]:.8f} {ys[i]:.8f} {(math.trunc(multi*zs[i])/multi):.3f}\n")
                    else:
                        fod.write(f"{xs[i]:.8f} {ys[i]:.8f} {zs[i]:.3f}\n")
                elif order == 'xzy':
                    if truncate:
                        fod.write(f"{xs[i]:.8f} {(math.trunc(multi*zs[i])/multi):.3f} {ys[i]:.8f}\n")
                    else:
                        fod.write(f"{xs[i]:.8f} {zs[i]:.3f} {ys[i]:.8f}\n")
                elif order == 'yxz':
                    if truncate:
                        fod.write(f"{ys[i]:.8f} {xs[i]:.8f} {(math.trunc(multi*zs[i])/multi):.3f}\n")
                    else:
                        fod.write(f"{ys[i]:.8f} {xs[i]:.8f} {zs[i]:.3f}\n")
                elif order == 'yzx':
                    if truncate:
                        fod.write(f"{ys[i]:.8f} {(math.trunc(multi*zs[i])/multi):.3f} {xs[i]:.8f}\n")
                    else:
                        fod.write(f"{ys[i]:.8f} {zs[i]:.3f} {xs[i]:.8f}\n")
                elif order == 'zxy':
                    if truncate:
                        fod.write(f"{(math.trunc(multi*zs[i])/multi):.3f} {xs[i]:.8f} {ys[i]:.8f}\n")
                    else:
                        fod.write(f"{zs[i]:.3f} {xs[i]:.8f} {ys[i]:.8f}\n")
                elif order == 'zyx':
                    if truncate:
                        fod.write(f"{(math.trunc(multi*zs[i])/multi):.3f} {ys[i]:.8f} {xs[i]:.8f}\n")
                    else:
                        fod.write(f"{zs[i]:.3f} {ys[i]:.8f} {xs[i]:.8f}\n")
                else:
                    raise  RuntimeError("unkown order: %s" % order)

        return True

    # aux methods

    def __repr__(self):
        msg = f"<{self.__class__.__name__}>\n"
        msg += f" <grid list[{len(self._grid_list)}]>\n"

        for path in self._grid_list:
            msg += f"  <{path}>\n"

        msg += f" <has current: {self.has_cur_grids}>\n"
        if self._cur_grids:
            msg += " <content>" + str(self._cur_grids)

        return msg
