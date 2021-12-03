from movdata import base
import datetime as dt
import math
import numpy as np
from osgeo import gdal
import tempfile
import os
import shutil
from joblib import Parallel, delayed
from joblib import load, dump
import movdata.raster as rst


class ETDAnalysisParams(base.AnalysisParams):

    def __init__(self,
                 maxdatagap_secs=14400,
                 maxspeed_kmhr=0.0,
                 maxspeed_percent=0.0,
                 intstep_kmhr=0.001,
                 etd_kernel=None,
                 prob_dens_cut_off=0.000001,
                 rast_params=None,
                 expansion_factor=1.3,
                 raster_storage=None):

        self._maxdatagap_secs = maxdatagap_secs
        self._maxspeed_kmhr = maxspeed_kmhr
        self._maxspeed_percent = maxspeed_percent
        self._intstep_kmhr = intstep_kmhr
        self._prob_dens_cut_off = prob_dens_cut_off
        self._etd_kernel = etd_kernel
        self._rast_params = rast_params
        self._expansion_factor = expansion_factor
        self._raster_storage = raster_storage


    @property
    def maxdatagap_secs(self):
        return self._maxdatagap_secs

    @property
    def maxspeed_kmhr(self):
        return self._maxspeed_kmhr

    @property
    def maxspeed_percent(self):
        return self._maxspeed_percent

    @property
    def intstep_kmhr(self):
        return self._intstep_kmhr

    @property
    def prob_dens_cut_off(self):
        return self._prob_dens_cut_off

    @property
    def rast_params(self):
        return self._rast_params

    @property
    def expansion_factor(self):
        return self._expansion_factor

    @property
    def raster_storage(self):
        return self._raster_storage

class ETDKernel:
    pass


class Weibull2Params(ETDKernel):

    def __init__(self,
                 shape=1.0,
                 scale=1.0):

        self._shape = shape
        self._scale = scale

    @property
    def scale(self):
        return self._scale

    @property
    def shape(self):
        return self._shape


class Weibull3Params(ETDKernel):
    """scale=a(t^b)(c^t) where t=time"""

    def __init__(self,
                 shape=1.0,
                 a=1.0,
                 b=1.0,
                 c=1.0):

        self._shape = shape
        self._a = a
        self._b = b
        self._c = c

    @property
    def scale(self):
        return self._scale

    @property
    def a(self):
        return self._a

    @property
    def b(self):
        return self._b

    @property
    def c(self):
        return self._c


class ETDAnalysisResult(base.AnalysisResult):

    def __init__(self, out_rast=None):
        self._out_rast = out_rast

    @property
    def out_rastdataset(self):
        return self._out_rast

    @out_rastdataset.setter
    def out_rastdataset(self, value):
        self._out_rast = value


class ETDAnalysis:

    @classmethod
    def calc_etd_range_parallel(cls, etd_analysis_params=None, trajectory=None):

        if __name__ != "__main__":
            # Create kde_analysis_result object
            etd_analysis_result = ETDAnalysisResult()
            etd_analysis_result.analysis_start = dt.datetime.utcnow()

            # Create a temporary folder
            folder = tempfile.mkdtemp()

            try:
                # Test to make sure the calculation parameters are not None and the correct type
                assert isinstance(etd_analysis_params, ETDAnalysisParams)

                # Make sure that the trajectory is not None
                if trajectory is None:
                    raise base.PymetException('KDE Analysis Error: Trajectory was None.')

                # Retrieve the Geopandas series for the trajectory
                traj_series = trajectory.relocs.as_geopandas_series()

                # Project to the desired output SRS
                if etd_analysis_params.rast_params.srs_code != 4326:
                    traj_series = traj_series.to_crs(epsg=etd_analysis_params.rast_params.srs_code)

                # Retrieve the x,y coordinates of the relocs into a numpy array
                traj_coords = np.array([[i[1].x, i[1].y] for i in traj_series.iteritems()])

                # Determine the envelope of the trajectory
                # env = trajectory.relocs().ogr_geometry().GetEnvelope()
                # x_min, x_max, y_min, y_max = env[0], env[1], env[2], env[3]
                (x_min, x_max, y_min, y_max) = trajectory.relocs.ogr_geometry.GetEnvelope()
                x_min = traj_coords[:, 0].min()
                x_max = traj_coords[:, 0].max()
                y_min = traj_coords[:, 1].min()
                y_max = traj_coords[:, 1].max()

                # Create a RasterProps object to define characteristics of the output raster
                raster_props = rst.RasterProps()

                # Determine the envelope wrt to the expansion_factor
                if etd_analysis_params.expansion_factor > 1.0:
                    dx = (x_max - x_min) * (etd_analysis_params.expansion_factor - 1.0) / 2.0
                    dy = (y_max - y_min) * (etd_analysis_params.expansion_factor - 1.0) / 2.0
                    x_min -= dx
                    x_max += dx
                    y_min -= dy
                    y_max += dy

                    # Determine the output raster size
                    num_columns = int(math.ceil((x_max - x_min) / etd_analysis_params.rast_params.pixel_size))
                    num_rows = int(math.ceil((y_max - y_min) / etd_analysis_params.rast_params.pixel_size))
                    # print('Columns & Rows:', num_columns, num_rows)

                    # Create the output raster file
                    driver = gdal.GetDriverByName('HFA')
                    outputpath = os.path.join(etd_analysis_params.raster_storage.location,
                                              etd_analysis_params.raster_storage.name)
                    output_raster = driver.Create(utf8_path=outputpath,
                                                  xsize=num_columns,
                                                  ysize=num_rows,
                                                  bands=1,
                                                  eType=gdal.GDT_Float64)

                    # Add the raster to the results object
                    etd_analysis_result.out_rastdataset = output_raster

                    # Define the affine transform for converting between grid coordinates and map coordinates
                    # needed by GDAL
                    transform_vals = (x_min, etd_analysis_params.rast_params.pixel_size, 0,
                                      y_max, 0, -etd_analysis_params.rast_params.pixel_size)
                    output_raster.SetGeoTransform(transform_vals)

                    # Get a hold of the raster output band
                    outband = output_raster.GetRasterBand(1)

                    # Set the NoData Value on the output band
                    outband.SetNoDataValue(etd_analysis_params.rast_params.no_data_value)

                    # Define the output_raster spatial reference
                    output_raster.SetProjection(base.SRS.srs_from_epsg
                                                (etd_analysis_params.rast_params.srs_code).ExportToWkt())

                    # Define the affine transform to get grid pixel centroids as geographic coordinates and adjusting
                    # the origin by a half pixel to the east and south from the grid origin point
                    img_centroids_to_map = np.array(transform_vals).reshape(2, 3)
                    img_centroids_to_map[0, 0] = x_min + etd_analysis_params.rast_params.pixel_size * 0.5
                    img_centroids_to_map[1, 0] = y_max - etd_analysis_params.rast_params.pixel_size * 0.5
                    # print(img_centroids_to_map)


            except base.PymetException as e:
                etd_analysis_result.add_error(e)

            finally:
                try:
                    shutil.rmtree(folder)
                except:
                    print("Failed to delete: " + folder)

            # Return the analysis kde_analysis_result
            etd_analysis_result.analysis_end = dt.datetime.utcnow()
            return etd_analysis_result  # return results