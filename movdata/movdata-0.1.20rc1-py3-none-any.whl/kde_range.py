import os
import tempfile
import math
import typing
import numpy as np
import datetime as dt
from movdata import base
import shutil
from pathlib import Path
from joblib import Parallel, delayed
from joblib import load, dump
from dataclasses import dataclass, field
import movdata.raster as rst


@dataclass(init=True, repr=True)
class KDEAnalysisProfile(base.AnalysisParams):
    """Defines the outline of KDE Analysis"""
    output_path: typing.Union[str, bytes, os.PathLike]
    smooth_param: float = 0.
    smooth_method: str = 'hRef'
    max_sd: float = 5.
    prob_dens_cut_off: float = 1E-15
    raster_profile: rst.RasterProfile = None
    expansion_factor: float = 1.
    _smooth_param: float = field(init=False, repr=False)

    def __post_init__(self):
        self.raster_profile = self.raster_profile

    @property
    def smooth_param(self):
        return self._smooth_param

    @smooth_param.setter
    def smooth_param(self, value):
        self._smooth_param = value


class KDEAnalysisResult(base.AnalysisResult):

    def __init__(self, out_rast=None):
        super().__init__()
        self._out_rast = out_rast

    @property
    def out_rastdataset(self):
        return self._out_rast

    @out_rastdataset.setter
    def out_rastdataset(self, value):
        self._out_rast = value


class KDEAnalysis:

    @classmethod
    def calculate_kde_range(cls, kde_profile: KDEAnalysisProfile, relocations: base.Relocations):
        assert isinstance(kde_profile, KDEAnalysisProfile)

        folder = tempfile.mkdtemp()
        kde_result = KDEAnalysisResult()
        kde_result.analysis_start = dt.datetime.utcnow()

        try:
            # reproject relocs to desired crs
            relocs = relocations.to_crs(kde_profile.raster_profile.crs)

            # retrieve the (x,y) coordinates of relocs into numpy array
            relocs_coords = np.column_stack((relocs.geometry.x, relocs.geometry.y))

            # Determine the envelope of the relocations
            x_min, y_min, x_max, y_max = relocs.geometry.total_bounds

            # apply expansion factor on the relocation total bound.
            if kde_profile.expansion_factor > 1.0:
                dx = (x_max - x_min) * (kde_profile.expansion_factor - 1.0) / 2.0
                dy = (y_max - y_min) * (kde_profile.expansion_factor - 1.0) / 2.0
                x_min -= dx
                x_max += dx
                y_min -= dy
                y_max += dy

            # update the raster extent for the raster profile
            kde_profile.raster_profile.raster_extent = rst.RasterExtent(x_min=x_min,
                                                                        x_max=x_max,
                                                                        y_min=y_min,
                                                                        y_max=y_max)

            # determine the output raster size
            num_rows, num_columns = kde_profile.raster_profile.rows, kde_profile.raster_profile.columns

            # Define the affine transform to get grid pixel centroids as geographic coordinates and adjusting
            # the origin by a half pixel to the east and south from the grid origin point
            img_centroids_to_map = np.array(kde_profile.raster_profile.transform.to_gdal()).reshape(2, 3)
            img_centroids_to_map[0, 0] = x_min + kde_profile.raster_profile.pixel_size * 0.5
            img_centroids_to_map[1, 0] = y_max - kde_profile.raster_profile.pixel_size * 0.5

            # Calculate smoothing parameter.
            if kde_profile.smooth_param == 0.0:
                if kde_profile.smooth_method == 'hRef':
                    kde_profile.smooth_param = cls.calc_hRef_smooth_param(x=relocs_coords[:, 0], y=relocs_coords[:, 1])
                else:
                    raise TypeError(f'KDEAnalysis Error: {kde_profile.smooth_method} is not supported.')
            if kde_profile.smooth_param == 0.0:
                raise base.PymetException('KDEAnalysis Error: smoothing parameter is zero.')

            # define scaling parameter
            outer_scaling_const = 1.0 / (relocs.shape[0] *
                                         kde_profile.smooth_param *
                                         kde_profile.smooth_param)

            inner_scaling_const = 1.0 / (2.0 * np.pi)

            # define max distance value
            variance = 2.0 * kde_profile.smooth_param * kde_profile.smooth_param
            max_dist = math.pow(kde_profile.max_sd, 2.0) * variance

            # create a temporary file for storing memmap files.
            relocs_coords_tmp = os.path.join(folder, 'traj_coords.mmap')
            raster_ndarray_tmp = os.path.join(folder, 'raster_ndarray.mmap')

            # Create a blank grid array and dump the data array to memmap to speedup the parallel process.
            raster_ndarray = np.zeros(shape=(num_rows, num_columns), dtype=np.float64)
            dump(raster_ndarray, raster_ndarray_tmp)
            raster_ndarray = load(raster_ndarray_tmp, mmap_mode='w+')

            if len(relocs_coords) >= 100000:
                # Dump the trajectory coordinates to disk to free the memory
                dump(relocs_coords, relocs_coords_tmp)

                # Release the reference on the original in memory array and replace it
                # by a reference to the memmap array so that the garbage collector can
                # release the memory before forking. gc.collect() is internally called
                # in Parallel just before forking.
                relocs_coords = load(relocs_coords_tmp, mmap_mode='r')

            # Fork the worker processes to perform computation concurrently
            parameters = ((i, j, raster_ndarray, img_centroids_to_map,
                           relocs_coords,
                           max_dist,
                           inner_scaling_const,
                           outer_scaling_const,
                           variance) for i in range(num_rows)
                          for j in range(num_columns))

            Parallel(n_jobs=-1, verbose=8)(delayed(cls.raster_calc)(*p) for p in parameters)

            # Normalize the grid values
            raster_ndarray = raster_ndarray / raster_ndarray.sum()

            # write raster_ndarray to GeoTIFF file.
            rst.RasterPy.write(ndarray=raster_ndarray, fp=kde_profile.output_path, **kde_profile.raster_profile)

        except base.PymetException as exc:
            kde_result.add_error(exc)
        finally:
            shutil.rmtree(folder, ignore_errors=True)

            # Return the analysis kde_analysis_result
            kde_result.analysis_end = dt.datetime.utcnow()
            return kde_result

    @classmethod
    def calc_hRef_smooth_param(cls, x=None, y=None):
        if x is None:
            return
        if y is None:
            return
        varX = x.var()
        varY = y.var()
        var = math.sqrt(0.5 * (varX + varY))
        t = math.pow(len(x), -1.0 / 6.0)
        hRef = var * t  # Source: Worton_1989
        return hRef

    @classmethod
    def raster_calc(cls, i=0, j=0, raster_ndarray=None, img_centroids_to_map=None, traj_coords=None,
                    max_dist=None, inner_scaling_constant=None, outer_scaling_constant=None, variance=None):
        """
        Loop over each pixel in the grid, transform the pixel coordinates (row, column) into
        geographic coordinates (i.e., the centroid of the pixel). For each pixel, loop through the
        relocation points and add the KDE density contribution to the pixel value.
        """

        # # Define the grid pixel coords:  [1, Pixel (column), Line (row)]
        pixel_coords = np.array([1, j, i]).reshape(3, 1)

        # Get the current pixel centroid coordinates
        centroid = np.dot(img_centroids_to_map, pixel_coords).flatten()

        coordinate_distances = np.subtract(traj_coords[:, 0], centroid[0]) ** 2 + \
                               np.subtract(traj_coords[:, 1], centroid[1]) ** 2

        # Set flag for elements that meet out max-dist criteria.
        # ...and then eliminate the distances outside that threshold
        low_v = coordinate_distances <= max_dist
        coordinate_distances = coordinate_distances[low_v]

        # Create exponents from distance values.
        coordinate_distances = coordinate_distances * -1 / variance

        # Exp.
        coordinate_distances = np.exp(coordinate_distances)

        # Scalar sum of array.
        theta_accumulator = np.sum(coordinate_distances)

        # Set value in shared array (with scaling constant).
        raster_ndarray.itemset((i, j), raster_ndarray[i, j] + theta_accumulator * outer_scaling_constant)
