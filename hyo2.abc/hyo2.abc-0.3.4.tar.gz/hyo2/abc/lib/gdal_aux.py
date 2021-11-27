from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import pyproj

from typing import Optional
import os
import logging

from hyo2.abc.lib.helper import Helper

logger = logging.getLogger(__name__)


class GdalAux:
    """ Auxiliary class to manage GDAL stuff """

    error_loaded = False
    gdal_data_fixed = False
    proj4_data_fixed = False

    ogr_formats = {
        'ESRI Shapefile': 0,
        'KML': 1,
        'CSV': 2,
    }

    ogr_exts = {
        'ESRI Shapefile': '.shp',
        'KML': '.kml',
        'CSV': '.csv',
    }

    @classmethod
    def current_gdal_version(cls) -> int:
        return int(gdal.VersionInfo('VERSION_NUM'))

    @classmethod
    def get_ogr_driver(cls, ogr_format):

        try:
            driver_name = [key for key, value in GdalAux.ogr_formats.items() if value == ogr_format][0]

        except IndexError:
            raise RuntimeError("Unknown ogr format: %s" % ogr_format)

        drv = ogr.GetDriverByName(driver_name)
        if drv is None:
            raise RuntimeError("Ogr failure > %s driver not available" % driver_name)

        return drv

    @classmethod
    def create_ogr_data_source(cls, ogr_format: str, output_path: str, epsg: Optional[int] = 4326):
        drv = cls.get_ogr_driver(ogr_format)
        output_file = output_path + cls.ogr_exts[drv.GetName()]
        # logger.debug("output: %s" % output_file)
        if os.path.exists(output_file):
            os.remove(output_file)

        ds = drv.CreateDataSource(output_file)
        if ds is None:
            raise RuntimeError("Ogr failure in creation of data source: %s" % output_path)

        if ogr_format == cls.ogr_formats['ESRI Shapefile']:
            cls.create_prj_file(output_path, epsg=epsg)

        return ds

    @classmethod
    def create_prj_file(cls, output_path: str, epsg: Optional[int] = 4326) -> None:
        """Create an ESRI lib file (geographic WGS84 by default)"""
        spatial_ref = osr.SpatialReference()
        spatial_ref.ImportFromEPSG(epsg)

        spatial_ref.MorphToESRI()
        fid = open(output_path + '.prj', 'w')
        fid.write(spatial_ref.ExportToWkt())
        fid.close()

    @staticmethod
    def list_ogr_drivers():
        """ Provide a list with all the available OGR drivers """

        cnt = ogr.GetDriverCount()
        driver_list = []

        for i in range(cnt):

            driver = ogr.GetDriver(i)
            driver_name = driver.GetName()
            if driver_name not in driver_list:
                driver_list.append(driver_name)

        driver_list.sort()  # Sorting the messy list of ogr drivers

        for i, drv in enumerate(driver_list):

            print("%3s: %25s" % (i, drv))

    @classmethod
    def gdal_error_handler(cls, err_class, err_num, err_msg) -> None:
        """GDAL Error Handler, to test it: gdal.Error(1, 2, b'test error')"""

        err_type = {
            gdal.CE_None: 'None',
            gdal.CE_Debug: 'Debug',
            gdal.CE_Warning: 'Warning',
            gdal.CE_Failure: 'Failure',
            gdal.CE_Fatal: 'Fatal'
        }
        try:
            err_msg = err_msg.replace('\n', ' ')
        except Exception as e:
            logger.warning("skip the new-line replacement: %s" % e)
        err_class = err_type.get(err_class, 'None')
        if err_class in ["Failure", "Fatal"]:
            raise RuntimeError("%s: gdal error %s > %s" % (err_class, err_num, err_msg))
        logger.info("%s: gdal error %s > %s" % (err_class, err_num, err_msg))

    @classmethod
    def push_gdal_error_handler(cls) -> None:
        """ Install GDAL error handler """
        if cls.error_loaded:
            return

        gdal.PushErrorHandler(cls.gdal_error_handler)

        gdal.UseExceptions()
        ogr.UseExceptions()
        osr.UseExceptions()

        cls.error_loaded = True

    @classmethod
    def check_gdal_data(cls):
        """ Check the correctness of os env GDAL_DATA """

        if cls.gdal_data_fixed:
            return

        if 'GDAL_DATA' in os.environ:

            # logger.debug("unset original GDAL_DATA = %s" % os.environ['GDAL_DATA'])
            del os.environ['GDAL_DATA']

        if 'GDAL_DRIVER_PATH' in os.environ:

            # logger.debug("unset original GDAL_DRIVER_PATH = %s" % os.environ['GDAL_DRIVER_PATH'])
            del os.environ['GDAL_DRIVER_PATH']

        gdal_data_path0 = os.path.join(os.path.dirname(gdal.__file__), 'osgeo', 'data', 'gdal')
        s57_agencies_csv_path0 = os.path.join(gdal_data_path0, 's57agencies.csv')
        if os.path.exists(s57_agencies_csv_path0):

            gdal.SetConfigOption('GDAL_DATA', gdal_data_path0)
            logger.debug("GDAL_DATA = %s" % gdal.GetConfigOption('GDAL_DATA'))
            cls.gdal_data_fixed = True
            cls.push_gdal_error_handler()
            return

        gdal_data_path1 = os.path.join(os.path.dirname(gdal.__file__), 'data', 'gdal')
        s57_agencies_csv_path1 = os.path.join(gdal_data_path1, 's57agencies.csv')
        if os.path.exists(s57_agencies_csv_path1):

            gdal.SetConfigOption('GDAL_DATA', gdal_data_path1)
            logger.debug("GDAL_DATA = %s" % gdal.GetConfigOption('GDAL_DATA'))
            cls.gdal_data_fixed = True
            cls.push_gdal_error_handler()
            return

        # anaconda specific (Win)
        gdal_data_path2 = os.path.join(Helper.python_path(), 'Library', 'data')
        s57_agencies_csv_path2 = os.path.join(gdal_data_path2, 's57agencies.csv')
        if os.path.exists(s57_agencies_csv_path2):

            gdal.SetConfigOption('GDAL_DATA', gdal_data_path2)
            logger.debug("GDAL_DATA = %s" % gdal.GetConfigOption('GDAL_DATA'))
            cls.gdal_data_fixed = True
            cls.push_gdal_error_handler()
            return

        # anaconda specific (Win)
        gdal_data_path3 = os.path.join(Helper.python_path(), 'Library', 'share', 'gdal')
        s57_agencies_csv_path3 = os.path.join(gdal_data_path3, 's57agencies.csv')
        if os.path.exists(s57_agencies_csv_path3):

            gdal.SetConfigOption('GDAL_DATA', gdal_data_path3)
            logger.debug("GDAL_DATA = %s" % gdal.GetConfigOption('GDAL_DATA'))
            cls.gdal_data_fixed = True
            cls.push_gdal_error_handler()
            return

        # anaconda specific (Linux)
        gdal_data_path4 = os.path.join(Helper.python_path(), 'share', 'gdal')
        s57_agencies_csv_path4 = os.path.join(gdal_data_path4, 's57agencies.csv')
        if os.path.exists(s57_agencies_csv_path4):

            gdal.SetConfigOption('GDAL_DATA', gdal_data_path4)
            logger.debug("GDAL_DATA = %s" % gdal.GetConfigOption('GDAL_DATA'))
            cls.gdal_data_fixed = True
            cls.push_gdal_error_handler()
            return

        # TODO: add more cases to find GDAL_DATA

        raise RuntimeError("Unable to locate GDAL data at:\n- %s\n- %s\n- %s\n- %s\n- %s"
                           % (gdal_data_path0, gdal_data_path1, gdal_data_path2, gdal_data_path3, gdal_data_path4))

    @classmethod
    def check_proj4_data(cls):
        """ Check the correctness of os env PROJ_LIB """

        if cls.proj4_data_fixed:
            return

        if hasattr(pyproj, 'pyproj_datadir'):
            # noinspection PyTypeChecker
            proj_path = os.path.join(pyproj.pyproj_datadir, "epsg")
            if os.path.exists(proj_path):
                # logger.debug("PROJ_LIB = %s" % proj_path)
                return

        if 'PROJ_LIB' in os.environ:

            # logger.debug("unset original PROJ_LIB = %s" % os.environ['PROJ_LIB'])
            del os.environ['PROJ_LIB']

        proj4_data_path1 = os.path.join(os.path.dirname(pyproj.__file__), 'data')
        epsg_path1 = os.path.join(proj4_data_path1, 'epsg')
        if os.path.exists(epsg_path1):

            os.environ['PROJ_LIB'] = proj4_data_path1
            if hasattr(pyproj, 'pyproj_datadir'):
                pyproj.pyproj_datadir = proj4_data_path1
            # logger.debug("PROJ_LIB = %s" % os.environ['PROJ_LIB'])
            cls.proj4_data_fixed = True
            return

        # anaconda specific (Win)
        proj4_data_path2 = os.path.join(Helper.python_path(), 'Library', 'data')
        epsg_path2 = os.path.join(proj4_data_path2, 'epsg')
        if os.path.exists(epsg_path2):

            os.environ['PROJ_LIB'] = proj4_data_path2
            if hasattr(pyproj, 'pyproj_datadir'):
                pyproj.pyproj_datadir = proj4_data_path2
            # logger.debug("PROJ_LIB = %s" % os.environ['PROJ_LIB'])
            cls.proj4_data_fixed = True
            return

        # anaconda specific (Win)
        proj4_data_path3 = os.path.join(Helper.python_path(), 'Library', 'share')
        epsg_path3 = os.path.join(proj4_data_path3, 'epsg')
        if os.path.exists(epsg_path3):

            os.environ['PROJ_LIB'] = proj4_data_path3
            if hasattr(pyproj, 'pyproj_datadir'):
                pyproj.pyproj_datadir = proj4_data_path3
            # logger.debug("PROJ_LIB = %s" % os.environ['PROJ_LIB'])
            cls.proj4_data_fixed = True
            return

        # anaconda specific (Linux)
        proj4_data_path4 = os.path.join(Helper.python_path(), 'share')
        epsg_path4 = os.path.join(proj4_data_path4, 'epsg')
        if os.path.exists(epsg_path4):

            os.environ['PROJ_LIB'] = proj4_data_path4
            if hasattr(pyproj, 'pyproj_datadir'):
                pyproj.pyproj_datadir = proj4_data_path4
            # logger.debug("PROJ_LIB = %s" % os.environ['PROJ_LIB'])
            cls.proj4_data_fixed = True
            return

        # anaconda specific (Linux)
        proj4_data_path5 = os.path.join(Helper.python_path(), 'share', 'proj')
        proj_db_path5 = os.path.join(proj4_data_path5, 'proj.db')
        if os.path.exists(proj_db_path5):

            os.environ['PROJ_LIB'] = proj4_data_path5
            if hasattr(pyproj, 'pyproj_datadir'):
                pyproj.pyproj_datadir = proj4_data_path5
            # logger.debug("PROJ_LIB = %s" % os.environ['PROJ_LIB'])
            cls.proj4_data_fixed = True
            return

        # anaconda specific (Win)
        proj4_data_path6 = os.path.join(Helper.python_path(), 'Library', 'share', 'proj')
        proj_db_path6 = os.path.join(proj4_data_path6, 'proj.db')
        if os.path.exists(proj_db_path6):

            os.environ['PROJ_LIB'] = proj4_data_path6
            if hasattr(pyproj, 'pyproj_datadir'):
                pyproj.pyproj_datadir = proj4_data_path6
            # logger.debug("PROJ_LIB = %s" % os.environ['PROJ_LIB'])
            cls.proj4_data_fixed = True
            return

        try:
            # noinspection PyUnresolvedReferences
            import conda

            conda_file_dir = conda.__file__
            conda_dir = conda_file_dir.split('lib')[0]
            proj4_data_path999 = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
            epsg_path999 = os.path.join(proj4_data_path999, 'epsg')
            if os.path.exists(epsg_path999):

                os.environ['PROJ_LIB'] = proj4_data_path999
                if hasattr(pyproj, 'pyproj_datadir'):
                    pyproj.pyproj_datadir = proj4_data_path999
                # logger.debug("PROJ_LIB = %s" % os.environ['PROJ_LIB'])
                cls.proj4_data_fixed = True
                return

        except Exception as e:
            logger.warning("%s" % e)

        # TODO: add more cases to find PROJ_LIB

        raise RuntimeError("Unable to locate PROJ4 data at:\n- %s\n- %s\n- %s\n- %s\n- %s\n- %s\n- Conda/share/proj"
                           % (proj4_data_path1, proj4_data_path2, proj4_data_path3, proj4_data_path4, proj4_data_path5,
                              proj4_data_path6))

    @classmethod
    def crs_id(cls, wkt: str) -> Optional[int]:
        srs = osr.SpatialReference()
        srs.ImportFromWkt(wkt)
        srs.AutoIdentifyEPSG()
        return srs.GetAuthorityCode(None)

    @classmethod
    def lat_long_to_zone_number(cls, lat, long):
        if 56 <= lat < 64 and 3 <= long < 12:
            return 32

        if 72 <= lat <= 84 and long >= 0:
            if long < 9:
                return 31
            elif long < 21:
                return 33
            elif long < 33:
                return 35
            elif long < 42:
                return 37

        return int((long + 180) / 6) + 1

    @classmethod
    def save_prj_file(cls, output_path: str, ds: gdal.Dataset) -> bool:
        src_srs = osr.SpatialReference()
        src_srs.ImportFromWkt(ds.GetProjection())
        src_srs.MorphToESRI()
        src_wkt = src_srs.ExportToWkt()

        prj_file = open(os.path.splitext(output_path)[0] + '.prj', 'wt')
        prj_file.write(src_wkt)
        prj_file.close()
        return True
