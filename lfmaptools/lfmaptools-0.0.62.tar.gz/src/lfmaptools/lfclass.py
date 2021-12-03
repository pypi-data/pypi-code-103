
import sys
import os
import shutil
import glob
import itertools
import warnings
import numpy as np
from numpy.lib.recfunctions import rename_fields as np_rename_fields
from numpy.lib.recfunctions import append_fields as np_append_fields
from scipy.interpolate import griddata
from shapely import wkt
from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon, LineString, MultiLineString, LinearRing, box, mapping, shape
from shapely.ops import transform, linemerge, unary_union, polygonize
from shapely.affinity import translate
import pandas as pd
import geopandas as gpd
import rasterio as rio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.windows import get_data_window
import xarray as xa
import rioxarray as rxa
import pyproj as Proj
from functools import partial
import contextily as ctx
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.legend as mlegend
from matplotlib.collections import PatchCollection
from matplotlib.path import Path
from matplotlib.textpath import TextToPath
from matplotlib.font_manager import FontProperties
from mpl_toolkits.axes_grid1 import make_axes_locatable
import webbrowser

from skimage.measure import find_contours
from scipy.interpolate import interp1d
import jenkspy

import zipfile
import tarfile
import gzip
import netCDF4 as nc
import utm
import numbers
import osmnx as osm
import folium
from xarray.core import variable

from lfmaptools.utilities import (_nice_round,
                                  _represents_int,
                                  latlon_to_utm_epsg,
                                  _path_of_file_in_zip,
                                  csv_active_cols,
                                  csv_num_cols,
                                  _decompress_gz)
from lfmaptools.netcdf_utils import nc2np, nc_max, nc_min, nc_min_max
from lfmaptools.geotools import EastingNorthing_TM, LatLon_TM_polygonize, LatLon_TM
from lfmaptools.demtools import load_dem, load_hillshade
from lfmaptools.epsg_defs import webmerc, wgs84
from lfmaptools.mapping import add_stamen_basemap
from lfmaptools.interptools import interp_weights, interpolate

_LFoutput_fmt = [
    {'file': 'all', 'column': 0, 'short_name': 'tile', 'long_name': 'tile id', 'symbol': None, 'units': 'dimensionless', 'dtype': int, 'infile': True, },
    {'file': 'all', 'column': 1, 'short_name': 'x_distance', 'long_name': 'Easting distance from origin at the domain centre', 'symbol': 'x', 'units': 'm', 'dtype': 'real', 'infile': True, },
    {'file': 'all', 'column': 2, 'short_name': 'y_distance', 'long_name': 'Northing distance from origin at the domain centre', 'symbol': 'y', 'units': 'm', 'dtype': 'real', 'infile': True, },
    {'file': 'all', 'column': 3, 'short_name': 'latitude', 'long_name': 'Latitude in WGS84 coordinates', 'symbol': 'lat', 'units': 'decimal degrees', 'dtype': 'real', 'infile': True, },
    {'file': 'all', 'column': 4, 'short_name': 'longitude', 'long_name': 'Longitude in WGS84 coordinates', 'symbol': 'lon', 'units': 'decimal degrees', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 5, 'short_name': 'flow_depth', 'long_name': 'Depth of lahar', 'symbol': 'h', 'units': 'm', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 6, 'short_name': 'flow_speed', 'long_name': 'Speed of lahar', 'symbol': '√(u^2+v^2)', 'units': 'm/s', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 7, 'short_name': 'mass_per_unit_area', 'long_name': 'Mass of lahar per unit area', 'symbol': 'ρh', 'units': 'kg/m^2', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 8, 'short_name': 'x_flux', 'long_name': 'Mass flux in the easting per unit length', 'symbol': 'ρhu', 'units': 'kg/m/s', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 9, 'short_name': 'y_flux', 'long_name': 'Mass flux in the northing per unit length', 'symbol': 'ρhv', 'units': 'kg/m/s', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 10, 'short_name': 'mass_of_solids', 'long_name': 'Mass of solids per unit area', 'symbol': 'ρhc', 'units': 'kg/m^2', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 11, 'short_name': 'base_elevation', 'long_name': 'Base topographic elevation', 'symbol': 'b0', 'units': 'm (a.s.l.)', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 12, 'short_name': 'base_x_slope', 'long_name': 'Slope of base topography in Easting', 'symbol': '∂b0/∂x', 'units': 'dimensionless', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 13, 'short_name': 'base_y_slope', 'long_name': 'Slope of base topography in Northing', 'symbol': '∂b0/∂y', 'units': 'dimensionless', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 14, 'short_name': 'elevation_change', 'long_name': 'Change in topographic elevation', 'symbol': 'bt', 'units': 'm', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 15, 'short_name': 'change_in_x_slope', 'long_name': 'Change in x-slope of topography', 'symbol': '∂bt/∂x', 'units': 'dimensionless', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 16, 'short_name': 'change_in_y_slope', 'long_name': 'Change in y-slope of topography', 'symbol': '∂bt/∂y', 'units': 'dimensionless', 'dtype': 'real', 'infile': True, },
    {'file': 'snapshot', 'column': 17, 'short_name': 'land_use', 'long_name': 'Land use category', 'symbol': ' ', 'units': 'dimensionless', 'dtype': 'int', 'infile': True, },
    {'file': 'snapshot', 'column': None, 'short_name': 'concentration', 'long_name': 'Solid mass concentration', 'symbol': 'c', 'units': 'dimensionless', 'dtype': 'real', 'infile': False, },
    {'file': 'MaxHeights.txt', 'column': 5, 'short_name': 'maximum_depth', 'long_name': 'Maximum depth of lahar', 'symbol': 'maxh', 'units': 'm', 'dtype': 'real', 'infile': True, },
    {'file': 'MaxHeights.txt', 'column': 6, 'short_name': 'time_of_maximum', 'long_name': 'Time of the maximum depth', 'symbol': 't_maxh', 'units': 's', 'dtype': 'real', 'infile': True, },
    {'file': 'MaxSpeeds.txt', 'column': 5, 'short_name': 'maximum_speed', 'long_name': 'Maximum speed of lahar', 'symbol': 'maxspd', 'units': 'm/s', 'dtype': 'real', 'infile': True, },
    {'file': 'MaxSpeeds.txt', 'column': 6, 'short_name': 'time_of_maximum', 'long_name': 'Time of the maximum speed', 'symbol': 't_maxspd', 'units': 's', 'dtype': 'real', 'infile': True, },
    {'file': 'MaxEorsion.txt', 'column': 5, 'short_name': 'maximum_erosion', 'long_name': 'Maximum erosion', 'symbol': 'maxero', 'units': 'm', 'dtype': 'real', 'infile': True, },
    {'file': 'MaxEorsion.txt', 'column': 6, 'short_name': 'time_of_maximum', 'long_name': 'Time of the maximum erosion', 'symbol': 't_maxero', 'units': 's', 'dtype': 'real', 'infile': True, },
    {'file': 'InundationTime.txt', 'column': 5, 'short_name': 'inundation_time', 'long_name': 'Time of first inundation', 'symbol': 't_inun', 'units': 's', 'dtype': 'real', 'infile': True, },
    {'file': 'Maximums.nc', 'short_name': 'maximum_depth', 'long_name': 'Maximum depth of lahar', 'symbol': 'maxh', 'units': 'm', 'dtype': 'real', 'infile': True, },
    {'file': 'Maximums.nc', 'short_name': 'time_of_max_depth', 'long_name': 'Time of the maximum depth', 'symbol': 't_maxh', 'units': 's', 'dtype': 'real', 'infile': True, },
    {'file': 'Maximums.nc', 'short_name': 'maximum_speed', 'long_name': 'Maximum speed of lahar', 'symbol': 'maxspd', 'units': 'm/s', 'dtype': 'real', 'infile': True, },
    {'file': 'Maximums.nc', 'short_name': 'time_of_max_erosion', 'long_name': 'Time of the maximum erosion depth', 'symbol': 't_maxe', 'units': 's', 'dtype': 'real', 'infile': True, },{'file': 'Maximums.nc', 'short_name': 'time_of_max_speed', 'long_name': 'Time of the maximum speed', 'symbol': 't_maxspd', 'units': 's', 'dtype': 'real', 'infile': True, },
    {'file': 'Maximums.nc', 'short_name': 'maximum_erosion', 'long_name': 'Maximum erosion depth', 'symbol': 'maxe', 'units': 'm', 'dtype': 'real', 'infile': True, },
    {'file': 'Maximums.nc', 'short_name': 'time_of_max_erosion', 'long_name': 'Time of the maximum erosion depth', 'symbol': 't_maxe', 'units': 's', 'dtype': 'real', 'infile': True, },
    {'file': 'Maximums.nc', 'short_name': 'maximum_concentration', 'long_name': 'Maximum concentration', 'symbol': 'maxc', 'units': '', 'dtype': 'real', 'infile': True, },
    {'file': 'Maximums.nc', 'short_name': 'time_of_max_concentration', 'long_name': 'Time of the maximum concentration', 'symbol': 't_maxc', 'units': 's', 'dtype': 'real', 'infile': True, },
    {'file': 'Maximums.nc', 'short_name': 'inundation_time', 'long_name': 'Time of first inundation', 'symbol': 't_inun', 'units': 's', 'dtype': 'real', 'infile': True, },
]
_LFoutput_shortnames = [d['short_name'] for d in _LFoutput_fmt]
def _get_LF_output_fmt(short_name, filetype='snapshot'):
    try:
        ret = next(item for item in _LFoutput_fmt if item['short_name'] == short_name and item['file'] in [filetype, 'all'])
    except:
        warnings.warn('Item {} not in known output formats for filetype {}'.format(short_name, filetype))
        ret = {'file': 'unknown', 'short_name': short_name, 'long_name': short_name.replace('_', ' '), 'symbol': '', 'units': '', 'dtype': '', 'infile': True, }
    return ret

class LFSource(object):
    def __init__(self, x=None, y=None, lat=None, lon=None, radius=None, time=None, flux=None, conc=None):
        self.x = x
        self.y = y
        self.lat = lat
        self.lon = lon
        self.radius = radius
        self.time = time
        self.flux = flux
        self.conc = conc

    def volume(self):
        return np.trapz(self.flux, self.time)

    def peak_flux(self):
        return np.amax(self.flux)

    def peak_time(self):
        i = np.argmax(self.flux)
        return self.time[i]

    def duration(self):
        return self.time[-1]-self.time[0]

class LaharFlowData(object):
    def __init__(self,LaharFlowDir,zipped=False):

        if zipped:
            self.zipped = True
            if not os.path.exists(LaharFlowDir+'.zip'):
                print('File {} does not exist'.format(LaharFlowDir+'.zip'))
                self.dir = None
                return
            else:
                self.dir = LaharFlowDir
                self._zipref = zipfile.ZipFile(LaharFlowDir+'.zip',"r")
        else:
            self.zipped = False
            if not os.path.exists(LaharFlowDir):
                print('Directory {} does not exist'.format(LaharFlowDir))
                self.dir = None
                return
            else:
                self.dir = LaharFlowDir

        if zipped:
            infoFilePath = _path_of_file_in_zip('RunInfo.txt',self._zipref)[0]
            infoFile = self._zipref.extract(infoFilePath) #,path=self.dir)
        else:
            infoFile = os.path.join(LaharFlowDir,"RunInfo.txt")
            assert(os.path.isfile(infoFile)), 'Run info file {} does not exist'.format(infoFile)
        self.infoFile = infoFile

        self.sources = []

        with open(infoFile) as f:
            for ln, line in enumerate(f):
                if "Input file name" in line:
                    self.inputFile = (line.split(':',1)[1]).strip(' \t\n\r')
                if "Latitude of domain centre" in line:
                    self.clat = float(line.split('=',1)[1])
                if "Longitude of domain centre" in line:
                    self.clong = float(line.split('=',1)[1])
                if "Time step between outputs" in line:
                    self.dtout = float(line.split('=',1)[1])
                if "height threshold" in line:
                    self.hthres = float(line.split('=',1)[1])
                if "nTiles" in line:
                    self.nTiles = int(line.split('=',1)[1])
                if "nXtiles" in line:
                    self.nXtiles = int(line.split('=',1)[1])
                if "nYtiles" in line:
                    self.nYtiles = int(line.split('=',1)[1])
                if "nXpertile" in line:
                    self.nXpertile = int(line.split('=',1)[1])
                if "nYpertile" in line:
                    self.nYpertile = int(line.split('=',1)[1])
                if "Xtilesize" in line:
                    self.Xtilesize = float(line.split('=',1)[1])
                if "Ytilesize" in line:
                    self.Ytilesize = float(line.split('=',1)[1])
                if "xSize" in line:
                    self.xSize = float(line.split('=',1)[1])
                if "ySize" in line:
                    self.ySize = float(line.split('=',1)[1])
                if "nXPoints" in line:
                    self.nX = int(line.split('=',1)[1])
                if "nYPoints" in line:
                    self.nY = int(line.split('=',1)[1])
                if "deltaX" in line:
                    self.dX = float(line.split('=',1)[1])
                if "deltaY" in line:
                    self.dY = float(line.split('=',1)[1])
                if "Number of output files" in line:
                    self.Nout = int(line.split('=',1)[1])
                if "Last output file" in line:
                    self.lastOut = int(line.split('=',1)[1])
                if "end time" in line:
                    self.endTime = float(line.split('=',1)[1])
                if "Time step between outputs" in line:
                    self.dT = float(line.split('=',1)[1])
                if "rhow" in line:
                    self.rhow = float(line.split('=',1)[1])
                if "rhos" in line:
                    self.rhos = float(line.split('=',1)[1])
                if "Erosion depth" in line:
                    self.Edepth = float(line.split('=',1)[1])
                if "Topography type" in line:
                    TopoType = line.split('=',1)[1]
                    self.TopoType = TopoType.strip(' \t\n\r')
                if "Topography path" in line:
                    self.TopoPath = line.split('=',1)[1].strip(' \t\n\r')
                if "Raster path" in line:
                    self.RasterPath = line.split('=',1)[1].strip(' \t\n\r')
                if "Raster file" in line:
                    self.RasterFile = line.split('=',1)[1].strip(' \t\n\r')
                if "SRTM path" in line:
                    self.SRTMPath = line.split('=',1)[1].strip(' \t\n\r')
                if "SRTM files" in line:
                    fileList=line.split('=',1)[1]
                    fileList=fileList.strip("\n")
                    fileList=fileList.strip()
                    SRTMFiles = fileList.split(",")
                    self.SRTMFiles = list(filter(None, SRTMFiles))
                if "SRTM virtual file" in line:
                    self.SRTMvrt = line.split('=',1)[1].strip(' \t\n\r')
                if "Embedded raster" in line:
                    if (line.split('=',1)[1].strip()=='on'):
                        self.embed = True
                    else:
                        self.embed = False
                if "Land use path" in line:
                    self.LandUsePath = line.split('=',1)[1].strip(' \t\n\r')
                if "Land use file" in line:
                    self.LandUseFile = line.split('=',1)[1].strip(' \t\n\r')
                if 'Source' in line:
                        s_x = float(next(f).split('=',1)[1].rstrip())
                        s_y = float(next(f).split('=',1)[1].rstrip())
                        s_lat = float(next(f).split('=',1)[1].rstrip())
                        s_lon = float(next(f).split('=',1)[1].rstrip())
                        s_radius = float(next(f).split('=',1)[1].rstrip())
                        s_time = np.fromstring(next(f).split('=',1)[1].rstrip().replace('(','').replace(')',''), sep=',')
                        s_flux = np.fromstring(next(f).split('=',1)[1].rstrip().replace('(','').replace(')',''), sep=',')
                        s_conc = np.fromstring(next(f).split('=',1)[1].rstrip().replace('(','').replace(')',''), sep=',')

                        self.sources.append(LFSource(x=s_x, y=s_y, lat=s_lat, lon=s_lon, radius=s_radius,
                                                     time=s_time, flux=s_flux, conc=s_conc))


            self.files=[]
            self.txt_files=[]
            self.tar_files=[]
            self.nc_files=[]
            self.gz_files=[]

            self.get_files()
            self.get_txt_files()
            self.get_nc_files()
            self.get_tar_files()
            self.get_gz_files()
            self.get_tiff_files()

            self.clatlong = [self.clat,self.clong]

            self.utm = utm.from_latlon(self.clat,self.clong)
            self.utmCode = latlon_to_utm_epsg(self.clat, self.clong)
            self.utmZone = utm.latlon_to_zone_number(self.clat,self.clong)

            if self.inputFile in self.files:
                self._get_parameters_from_inputfile()
            else:
                self._get_parameters_from_runinfo()

            if ('Maximums.nc' in self.nc_files):
                self._get_nc_max()
            else:
                self._get_max_depth()
                self._get_max_speed()
                self._get_max_conc()
                self._get_max_bed_evolution()

    def _get_parameters_from_inputfile(self):
        if self.zipped:
            inputFileName = os.path.split(self.inputFile)[-1]
            inputFilePath = _path_of_file_in_zip(inputFileName, self._zipref)[0]
            inputFile = self._zipref.extract(inputFilePath,path=self.dir)
        else:
            inputFile = os.path.join(self.dir,os.path.split(self.inputFile)[1])
            if not os.path.isfile(inputFile):
                print('Input file {} does not exist'.format(inputFile))
                return
        parameters = []
        with open(inputFile) as f:
            for line in f:
                try:
                    keyword,value = line.split('=',2)
                    keyword = keyword.rstrip()
                    value = value.rstrip()
                    if keyword=="Drag":
                        self.Drag = value
                        parameters.append('Drag')
                    if keyword=="Chezy co":
                        self.Chezy_co = float(value)
                        parameters.append('Chezy_co')
                    if keyword=="Pouliquen min":
                        self.Pouliquen_min = float(value)
                        parameters.append('Pouliquen_min')
                    if keyword=="Pouliquen max":
                        self.Pouliquen_max = float(value)
                        parameters.append('Pouliquen_max')
                    if keyword=="Pouliquen delta":
                        self.Pouliquen_delta = float(value)
                        parameters.append('Pouliquen_delta')
                    if keyword=="Pouliquen beta":
                        self.Pouliquen_beta = float(value)
                        parameters.append('Pouliquen_beta')
                    if keyword=="Pouliquen L on d":
                        self.Pouliquen_L_on_d = float(value)
                        parameters.append('Pouliquen_L_on_d')
                    if keyword=="Erosion Rate":
                        self.ErosionRate = float(value)
                        parameters.append('ErosionRate')
                    if keyword=="Granular Erosion Rate":
                        self.GranularErosionRate = float(value)
                        parameters.append('GranularErosionRate')
                    if keyword=="Erosion depth":
                        self.ErosionDepth = float(value)
                        parameters.append('ErosionDepth')
                    if keyword=="Erosion critical Eond":
                        self.ErosionCritical_E_on_d = float(value)
                        parameters.append('ErosionCritical_E_on_d')
                    if keyword=="Voellmy switch rate":
                        self.Voellmy_switch_rate = float(value)
                        parameters.append('Voellmy_switch_rate')
                    if keyword=="VoellmySwitch on maxPack":
                        self.VoellmySwitch_on_maxPack = float(value)
                        parameters.append('VoellmySwitch_on_maxPack')
                    if keyword=="Bed porosity":
                        self.Bed_porosity = float(value)
                        parameters.append('Bed_porosity')
                    if keyword=="Voellmy switch value":
                        self.Voellmy_switch_value = float(value)
                        parameters.append('Voellmy_switch_value')
                    if keyword=="maxPack":
                        self.maxPack = float(value)
                        parameters.append('maxPack')
                    if keyword=="rhow":
                        self.rhow = float(value)
                        parameters.append('rhow')
                    if keyword=="rhos":
                        self.rhos = float(value)
                        parameters.append('rhos')
                    if keyword=="Erosion critical height":
                        self.Erosion_critical_height = float(value)
                        parameters.append('Erosion_critical_height')
                    if keyword=="Pouliquen L":
                        self.Pouliquen_L = float(value)
                        parameters.append('Pouliquen_L')
                    if keyword=="Solid diameter":
                        self.Solid_diameter = float(value)
                        parameters.append('Solid_diameter')

                except:
                    pass
        self.parameters = parameters

    def _get_parameters_from_runinfo(self):
        parameters = []

        with open(self.infoFile) as f:
            for line in f:
                delim = '=' if '=' in line else ':'
                try:
                    keyword,value = line.split(delim,1)
                    keyword = keyword.rstrip()
                    value = value.rstrip()
                    if keyword=="Drag":
                        self.Drag = value
                        parameters.append('Drag')
                    if keyword=="Chezy coefficient":
                        self.Chezy_co = float(value)
                        parameters.append('Chezy_co')
                    if keyword=="Pouliquen Min Slope":
                        self.Pouliquen_min = float(value)
                        parameters.append('Pouliquen_min')
                    if keyword=="Pouliquen Max Slope":
                        self.Pouliquen_max = float(value)
                        parameters.append('Pouliquen_max')
                    if keyword=="Erosion rate":
                        self.ErosionRate = float(value)
                        parameters.append('ErosionRate')
                    if keyword=="Granular erosion rate":
                        self.GranularErosionRate = float(value)
                        parameters.append('GranularErosionRate')
                    if keyword=="Erosion depth":
                        self.ErosionDepth = float(value)
                        parameters.append('ErosionDepth')
                    if keyword=="Voellmy switch rate":
                        self.Voellmy_switch_rate = float(value)
                        parameters.append('Voellmy_switch_rate')
                    if keyword=="Bed porosity":
                        self.Bed_porosity = float(value)
                        parameters.append('Bed_porosity')
                    if keyword=="Voellmy switch value":
                        self.Voellmy_switch_value = float(value)
                        parameters.append('Voellmy_switch_value')
                    if keyword=="Maximum packing fraction":
                        self.maxPack = float(value)
                        parameters.append('maxPack')
                    if keyword=="rhow":
                        self.rhow = float(value)
                        parameters.append('rhow')
                    if keyword=="rhos":
                        self.rhos = float(value)
                        parameters.append('rhos')
                    if keyword=="Erosion critical height":
                        self.Erosion_critical_height = float(value)
                        parameters.append('Erosion_critical_height')
                    if keyword=="Solid diameter":
                        self.Solid_diameter = float(value)
                        parameters.append('Solid_diameter')
                    if keyword=="Erosion":
                        self.Erosion = value
                        parameters.append('Erosion')
                    if 'Source' in keyword:
                        s_x = float(next(f).split('=',1)[1].rstrip())
                        s_y = float(next(f).split('=',1)[1].rstrip())
                        s_lat = float(next(f).split('=',1)[1].rstrip())
                        s_lon = float(next(f).split('=',1)[1].rstrip())
                        s_radius = float(next(f).split('=',1)[1].rstrip())
                        s_time = np.fromstring(next(f).split('=',1)[1].rstrip().replace('(','').replace(')',''))
                        s_flux = np.fromstring(next(f).split('=',1)[1].rstrip().replace('(','').replace(')',''))
                        s_conc = np.fromstring(next(f).split('=',1)[1].rstrip().replace('(','').replace(')',''))

                        self.sources.append(LFSource(x=s_x, y=s_y, lat=s_lat, lon=s_lon, radius=s_radius,
                                                     time=s_time, flux=s_flux, conc=s_conc))
                except:
                    pass

        self.parameters = parameters

    def _grid_to_physical(self, grid_i, grid_j, tile_i, tile_j, x, y):

      x = -0.5 * self.xSize + self.dX * ((grid_i - 1.0) * self.nXpertile + (tile_i - 0.5))
      y = -0.5 * self.ySize + self.dY * ((grid_j - 1.0) * self.nYpertile + (tile_j - 0.5))

      return x, y

    def _tile_row(self, tile):

      row = (tile - 1) // self.nXtiles + 1

      return int(row)

    def _tile_col(self, tile):

      col = (tile - 1)%self.nXtiles + 1

      return int(col)

    def _grid_coords(self, tileID):

      i = self._tile_col(tileID)
      j = self._tile_row(tileID)

      return i, j

    def _tile_id(self, grid_i, grid_j):

        t = grid_i + (grid_j-1)*self.nXtiles
        return t

    def _neighbour_tiles(self, tile):

        i, j = self._grid_coords(tile)

        neighbours = []

        for k in [-1,1]:
            neighbours.append(self._tile_id(i+k, j))
            neighbours.append(self._tile_id(i, j+k))
            neighbours.append(self._tile_id(i+k, j+k))
            neighbours.append(self._tile_id(i+k, j-k))

        return neighbours

    def _connected_tiles(self, tiles):

        groups = [[tiles[0]]]

        tiles = tiles[1:]

        for t in tiles:
            neighbours = self._neighbour_tiles(t)

            in_group = False
            for group in groups:
                if any(n in group for n in neighbours):
                    group.append(t)
                    in_group = True
                    break

            if not in_group:
                groups.append([t])

        return groups

    def _tile_row_groups(self, tiles):

        rows = [self._tile_row(t) for t in tiles]

        ur = np.unique(rows)

        row_groups=[]
        for r in ur:
            row_groups.append([t for j, t in enumerate(tiles) if rows[j]==r])

        return row_groups

    def _get_latlon_res(self):

        East_step = LatLon_TM(self.clatlong, [self.dX, 0], unit='m')
        North_step = LatLon_TM(self.clatlong, [0, self.dY], unit='m')

        clat= self.clat
        clong = 360 + self.clong if self.clong<0 else self.clong

        lat_res = North_step[0] - clat
        lon_res = East_step[1] - clong

        # if clat<0:
        #     lat_res = -lat_res

        return (lat_res, lon_res)

    def EN_from_latlon(self, lat, lon):
        return np.array(EastingNorthing_TM(self.clatlong, (lat,lon)))

    def get_XY(self):

        x = ((np.arange(0,self.xSize,self.dX)-self.xSize/2)+self.dX/2)
        y = ((np.arange(0,self.ySize,self.dY)-self.ySize/2)+self.dY/2)

        return x, y

    def get_files(self):
        if self.zipped:
            files = self._zipref.namelist()
            self.files = [os.path.split(f)[1] for f in files]
        else:
            self.files = os.listdir(self.dir)

    def get_tar_files(self):
        self.tar_files = [f for f in self.files if f.endswith('.tar.gz')]
        self.tar_files.sort()

    def get_nc_files(self):
        self.nc_files = [f for f in self.files if f.endswith('.nc')]
        self.nc_files.sort()

    def get_gz_files(self):
        self.gz_files = [f for f in self.files if f.endswith('.gz')]
        self.gz_files.sort()

    def get_txt_files(self):
        self.txt_files = [f for f in self.files if f.endswith('.txt')]
        self.txt_files.sort()

    def get_tiff_files(self):
        self.tiff_files = [f for f in self.files if f.endswith('.tif') or f.endswith('.tiff')]
        self.tiff_files.sort()

    def _snapshot_txt_files(self):
        txt_files = [f for f in self.txt_files if f.strip('.txt').isnumeric()]
        txt_files.sort()
        return txt_files

    def _snapshot_nc_files(self):
        nc_files = [f for f in self.nc_files if f.strip('.nc').isnumeric()]
        nc_files.sort()
        return nc_files

    def get_snapshot_files(self):
        txt_files = [f.strip('.txt') for f in self.txt_files if f.strip('.txt').isnumeric()]
        nc_files = [f.strip('.nc') for f in self.nc_files if f.strip('.nc').isnumeric()]
        sfiles = list(set(txt_files + nc_files))
        sfiles.sort()
        return sfiles

    def _update_tiff_files(self,file,epsg=None):
        assert(file.endswith('tif')), 'In updateTiff, file must have a .tif extension; received {}'.format(file)

        n = len(self.tiffFiles)
        if epsg is None:
            with rio.open(os.path.join(self.dir,file)) as src:
                epsg = src.crs.to_epsg()
        self.tiffFiles[file] = {'file':file,'epsg':epsg,'index':n}
        return

    def _valid_input_file(self, fileIn):
        if isinstance(fileIn, str):
            if fileIn not in self.files:
                raise ValueError('Result file {file} is not in directory {dir}'.format(file=fileIn, dir=self.dir))
        elif isinstance(fileIn, int):
            if '{0:06d}.nc'.format(fileIn) in self.files:
                fileIn = '{0:06d}.nc'.format(fileIn)
            elif '{0:06d}.txt'.format(fileIn) in self.files:
                fileIn = '{0:06d}.txt'.format(fileIn)
            elif '{0:06d}.txt.tar.gz'.format(fileIn) in self.files:
                fileIn = '{0:06d}.txt.tar.gz'.format(fileIn)
            elif '{0:06d}.nc.gz'.format(fileIn) in self.files:
                fileIn = '{0:06d}.nc.gz'.format(fileIn)
            else:
                raise ValueError('Result file {file} is not in directory {dir}'.format(file=fileIn, dir=self.dir))
        else:
            raise RuntimeError("Result must be either the name of file in directory {dirc}, or an integer".format(dirc=self.dir))
        return fileIn

    def _file_type(self, filename):
        _ = self._valid_input_file(filename)
        if isinstance(filename, str):
            if filename=='MaxHeights.txt':
                filetype = 'MaxHeights.txt'
            elif filename=='MaxSpeeds.txt':
                filetype = 'MaxSpeeds.txt'
            elif filename=='InundationTime.txt':
                filetype = 'InundationTime.txt'
            elif filename=='Maximums.nc':
                filetype = 'Maximums.nc'
            else:
                filetype = 'snapshot'
        elif isinstance(filename, int):
            filetype = 'snapshot'

        return filetype

    def _valid_variable(self, variable):
        if variable not in _LFoutput_shortnames:
            raise RuntimeError('variable {var} not recognized'.format(var=variable))

    def _extract_file(self, filename):

        if self.zipped:
            LaharFlowFilePath = _path_of_file_in_zip(filename, self._zipref)[0]
            LaharFlowFile = self._zipref.extract(LaharFlowFilePath, path=self.dir)
            ExtractPath = os.path.join(self.dir, os.path.split(LaharFlowFilePath)[0])
        elif filename in self.txt_files:
            LaharFlowFile = os.path.join(self.dir, filename)
            ExtractPath = self.dir
        elif filename in self.nc_files:
            LaharFlowFile = os.path.join(self.dir, filename)
            ExtractPath = self.dir
        elif filename in self.tar_files:
            LaharFlowFile = os.path.join(self.dir, filename)
            ExtractPath = self.dir
        elif filename in self.gz_files:
            LaharFlowFile = os.path.join(self.dir, filename)
            ExtractPath = self.dir

        fname = os.path.split(LaharFlowFile)[1]

        if (fname in self.tar_files) and (fname not in self.txt_files):
            tar = tarfile.open(LaharFlowFile, mode='r')
            tar.extractall(path=ExtractPath)
            tar.close()
            self.get_txt_files()
            LaharFlowFile = '.'.join(LaharFlowFile.split('.')[:-2])
        elif (fname in self.gz_files) and (fname not in self.txt_files) and (fname not in self.nc_files):
            LaharFlowFile = _decompress_gz(LaharFlowFile)
            self.get_txt_files()
            self.get_nc_files()

        return LaharFlowFile

    def _get_data_column_names(self, filename):
        filename = self._valid_input_file(filename)
        LaharFlowFile = self._extract_file(filename)

        cols = csv_active_cols(LaharFlowFile)
        return cols

    def _get_data_txt(self, LaharFlowFile):
        try:
            cols = csv_active_cols(LaharFlowFile)
            data = np.genfromtxt(LaharFlowFile, delimiter=',', names=True, usecols=cols)
            return data
        except:
            raise RuntimeWarning('Unable to get data from {}'.format(LaharFlowFile))

    def _get_data_nc(self, LaharFlowFile):

        data = nc2np(LaharFlowFile)

        data = np_rename_fields(data, {'lat':'latitude', 'lon':'longitude'})

        return data

    def _get_data(self, filename):

        filename = self._valid_input_file(filename)

        LaharFlowFile = self._extract_file(filename)

        fileext = os.path.splitext(LaharFlowFile)[1]

        if fileext=='.txt':
            return self._get_data_txt(LaharFlowFile)
        elif fileext=='.nc':
            try:
                d = self._get_data_nc(LaharFlowFile)
            except:
                print('Could not load netcdf file '+LaharFlowFile)
                d = None
            return d
        else:
            raise ValueError('File {} not recognized'.format(LaharFlowFile))

    def latlon_in_data_extent(self, data, latlon):
        fields = data.dtype.names
        if 'latitude' not in fields:
            raise ValueError('latitude not in data array')
        if 'longitude' not in fields:
            raise ValueError('longitude not in data array')

        min_lat = data['latitude'].min()
        max_lat = data['latitude'].max()
        min_lon = data['longitude'].min()
        max_lon = data['longitude'].max()

        if latlon[0]<min_lat:
            return False
        if latlon[0]>max_lat:
            return False
        if latlon[1]<min_lon:
            return False
        if latlon[1]>max_lon:
            return False

        return True

    def xy_in_data_extent(self, data, xy):
        fields = data.dtype.names
        if 'x_distance' not in fields:
            raise ValueError('x_distance not in data array')
        if 'y_distance' not in fields:
            raise ValueError('y_distance not in data array')

        min_x = data['x_distance'].min()
        max_x = data['x_distance'].max()
        min_y = data['y_distance'].min()
        max_y = data['y_distance'].max()

        if xy[0]<min_x:
            return False
        if xy[0]>max_x:
            return False
        if xy[1]<min_y:
            return False
        if xy[1]>max_y:
            return False

        return True

    def raster(self, filename, var=None, full_domain=False, nodata=np.nan, masked=True, crs=None, res=None):

        filetype = self._file_type(filename)
        filename = self._valid_input_file(filename)

        # LaharFlowFile = self._extract_file(filename)
        # print (LaharFlowFile)

        # cols = csv_active_cols(LaharFlowFile)
        # data = np.genfromtxt(LaharFlowFile, delimiter=',', names=True, usecols=cols)
        data = self._get_data(filename)

        extra_cols = ['tile', 'x_distance', 'y_distance', 'latitude', 'longitude']
        if var is None:
            data_cols = [x for x in data.dtype.names
                            if x not in extra_cols]
        else:
            data_cols = [x for x in var]

        if filetype=='snapshot' and 'concentration' in data_cols:
            conc = np.divide(data['mass_of_solids'], data['mass_per_unit_area'], where=data['mass_per_unit_area']>1e-6)
            data = np_append_fields(data, 'concentration', conc, dtypes=np.float64)

        if res is None:
            res_lat, res_lon = self._get_latlon_res()
        else:
            if isinstance(res, float):
                res_lat = res
                res_lon = res
            elif isinstance(res, tuple) or isinstance(res, list):
                res_lat = res[0]
                res_lon = res[1]
            else:
                raise ValueError('res must be either a float or a tuple/list')

        tiles = data['tile'].astype(int)
        uTiles = np.unique(tiles)

        lats = data['latitude']
        lons = data['longitude']

        lat_pts = np.arange(lats.min(), lats.max()+res_lat, step=res_lat)
        lon_pts = np.arange(lons.min(), lons.max()+res_lon, step=res_lon)
        grid_lon, grid_lat = np.meshgrid(lon_pts, lat_pts)
        ds = xa.Dataset()
        ds.coords["latitude"] = lat_pts
        ds.coords["longitude"] = lon_pts
        xy = np.zeros([len(lats),2])
        xy[:,0] = lats
        xy[:,1] = lons
        uv = np.zeros([grid_lon.shape[0]*grid_lon.shape[1],2])
        uv[:,0] = grid_lat.flatten()
        uv[:,1] = grid_lon.flatten()
        vtx, wts = interp_weights(xy, uv)

        for d, col in enumerate(data_cols):
            vals = interpolate(data[col], vtx, wts)
            grid_data = vals.reshape(grid_lat.shape[0], grid_lat.shape[1])
         # grid_data = griddata((lats,lons), dat[col], (grid_lat, grid_lon), method='linear')
            ds[col] = (("latitude","longitude"), grid_data)
            fmt = _get_LF_output_fmt(col, filetype=filetype)
            ds[col].attrs["short_name"] = fmt['short_name']
            ds[col].attrs["long_name"] = fmt['long_name']
            ds[col].attrs["units"] = fmt['units']
            ds[col].attrs["symbol"] = fmt['symbol']
            ds[col].rio.write_nodata(np.nan, inplace=True)
        ds['latitude'].attrs["units"] = "degrees"
        ds['longitude'].attrs["units"] = "degrees"
        ds.rio.write_crs(wgs84, inplace=True)

        if crs is not None and crs is not wgs84:
            raster = ds.rio.reproject(crs)
        else:
            raster = ds

        return raster

        # tile_groups = self._connected_tiles(uTiles)

        # raster = [xa.Dataset()]*len(tile_groups)

        # for i, g in enumerate(tile_groups):

        #     ii = np.isin(tiles, g)

        #     dat = data[ii]

        #     lats = dat['latitude']
        #     lons = dat['longitude']

        #     lat_pts = np.arange(lats.min(), lats.max()+res_lat, step=res_lat)
        #     lon_pts = np.arange(lons.min(), lons.max()+res_lon, step=res_lon)

        #     grid_lon, grid_lat = np.meshgrid(lon_pts, lat_pts)

        #     ds = xa.Dataset()
        #     ds.coords["latitude"] = lat_pts
        #     ds.coords["longitude"] = lon_pts

        #     xy = np.zeros([len(lats),2])
        #     xy[:,0] = lats
        #     xy[:,1] = lons

        #     uv = np.zeros([grid_lon.shape[0]*grid_lon.shape[1],2])
        #     uv[:,0] = grid_lat.flatten()
        #     uv[:,1] = grid_lon.flatten()

        #     vtx, wts = interp_weights(xy, uv)

        #     for d, col in enumerate(data_cols):
        #         vals = interpolate(dat[col], vtx, wts)
        #         grid_data = vals.reshape(grid_lat.shape[0], grid_lat.shape[1])

        #         # grid_data = griddata((lats,lons), dat[col], (grid_lat, grid_lon), method='linear')
        #         ds[col] = (("latitude","longitude"), grid_data)
        #         fmt = _get_LF_output_fmt(col, filetype=filetype)
        #         ds[col].attrs["short_name"] = fmt['short_name']
        #         ds[col].attrs["long_name"] = fmt['long_name']
        #         ds[col].attrs["units"] = fmt['units']
        #         ds[col].attrs["symbol"] = fmt['symbol']
        #         ds[col].rio.write_nodata(np.nan, inplace=True)
        #     ds['latitude'].attrs["units"] = "degrees"
        #     ds['longitude'].attrs["units"] = "degrees"
        #     ds.rio.write_crs(wgs84, inplace=True)

        #     raster[i] = ds

        ## This could be useful, but doesn't work because of projection -- I think this needs to be fixed in laharflow
        # for i, g in enumerate(tile_groups):

        #     row_groups = self._tile_row_groups(g)

        #     for j, r in enumerate(row_groups):

        #         for k, t in enumerate(r):
        #             ds_tmp = xa.Dataset()
        #             ii = np.where(tiles==t)

        #             dat = data[ii]
        #             ds_tmp.coords["y"] = np.unique(dat['y_distance'])# + self.utm[1]
        #             ds_tmp.coords["x"] = np.unique(dat['x_distance'])# + self.utm[0]
        #             ds_tmp.coords['lat'] = (("y","x"), dat['latitude'].reshape(self.nYpertile, self.nXpertile))
        #             ds_tmp.coords['lon'] = (("y","x"), dat['longitude'].reshape(self.nYpertile, self.nXpertile))
        #             for d, col in enumerate(data_cols):
        #                 ds_tmp[col] = (("y","x"), dat[col].reshape(self.nYpertile, self.nXpertile))
        #                 fmt = _get_LF_output_fmt(col, filetype=filetype)
        #                 ds_tmp[col].attrs["short_name"] = fmt['short_name']
        #                 ds_tmp[col].attrs["long_name"] = fmt['long_name']
        #                 ds_tmp[col].attrs["units"] = fmt['units']
        #                 ds_tmp[col].attrs["symbol"] = fmt['symbol']
        #             ds_tmp.coords["Northing"] = (("y"), ds_tmp.y.data + self.utm[1])
        #             ds_tmp.coords["Easting"] = (("x"), ds_tmp.x.data + self.utm[0])


        #             if k==0:
        #                 row = ds_tmp
        #             else:
        #                 row = xa.combine_nested([[row], [ds_tmp]], concat_dim=['x','y'])

        #         if j==0:
        #             raster[i] = row
        #         else:
        #             raster[i] = xa.combine_nested([[raster[i], row]], concat_dim=['x','y'])

        #     raster[i].x.attrs["units"] = "metres"
        #     raster[i].y.attrs["units"] = "metres"

        #     raster[i] = raster[i].rio.write_crs(self.utmCode)


        # ds = xa.Dataset()
        # ds.coords["x"] = x0-1.5*self.dX + self.utm[0] # This seems to be right, but why??
        # ds.coords["y"] = y0-0.5*self.dY + self.utm[1]
        # for d, col in enumerate(data_cols):
        #     if np.isnan(nodata):
        #         dA[d].where(np.isnan(dA[d])==False, drop=True)
        #     else:
        #         dA[d].where(dA[d]==nodata, drop=True)
        #     ds[col] = dA[d]

        #     # ds[col] = (("y","x"), array[:,:,d])
        #     ds[col].rio.write_nodata(nodata, inplace=True)
        #     fmt = _get_LF_output_fmt(col, filetype=filetype)
        #     ds[col].attrs["short_name"] = fmt['short_name']
        #     ds[col].attrs["long_name"] = fmt['long_name']
        #     ds[col].attrs["units"] = fmt['units']
        #     ds[col].attrs["symbol"] = fmt['symbol']

        # return raster

    def _raster_flatten(self, raster, var):
        vals = raster[var].values.flatten()
        rflat = vals[~np.isnan(vals)]
        return rflat

    def _get_data_column(self, filename, data_col):

        dataFile = self._extract_file(filename)

        try:
            data = np.genfromtxt(dataFile,delimiter=',',comments='%',skip_header=1)
            x = data[:,1]
            y = data[:,2]
            d = data[:,data_col]
            return x, y, d
        except:
            return None, None, None

    def _data_to_array(self, x, y, data,
                       nodata=-1.0,
                       masked=True,
                       vmin=None,
                       full_domain=True):
        ux = np.unique(x)
        uy = np.unique(y)
        Nux = len(ux)
        Nuy = len(uy)
        if full_domain:
            x0, y0= self.get_XY()
            array = nodata*np.ones((self.nY,self.nX))
        else:
            x0 = ux
            y0 = uy
            array = nodata*np.ones((self.Nuy,self.Nux))

        for k in range(0,len(x)):
            xk = x[k]
            yk = y[k]
            ii = np.where(yk==y0)
            jj = np.where(xk==x0)
            if (vmin is None) or (data[k]>vmin):
                array[ii,jj] = data[k]

        if masked:
            array = np.ma.masked_where(array==nodata,array)
        return array

    def _get_max_bed_evolution(self):
        last_outfile = int(self.get_snapshot_files()[-1])

        data = self.raster(last_outfile, var=['elevation_change'])

        bt = data['elevation_change'].values

        MaxErosion = max(-np.nanmin(bt),0.0)
        MaxDeposit = max(np.nanmax(bt),0.0)

        self.MaxErosion = MaxErosion
        self.MaxDeposit = MaxDeposit
        return

    def max_bed_evolution(self, data=None, vmin=None, vmax=None):
        last_outfile = self.get_snapshot_files()[-1]

        if data is None:
            data = self.raster(last_outfile)
        if 'elevation_change' not in list(data.keys()):
            data = self.raster(last_outfile)

        bt = data['elevation_change']

        if vmin is not None:
            bt = bt.where(bt.data>vmin)

        if vmax is not None:
            bt = bt.where(bt.data<vmax)

        return bt

    def _get_nc_max(self):
        LaharFlowFile = self._extract_file('Maximums.nc')
        try:
            m = nc_max(LaharFlowFile)
            self.MaxDepth = m['maximum_depth']
            self.MaxSpeed = m['maximum_speed']
            self.MaxConc = m['maximum_concentration']
        except:
            self.MaxDepth = None
            self.MaxSpeed = None
            self.MaxConc = None

        last_outfile = self._snapshot_nc_files()[-1]
        LaharFlowFile = self._extract_file(last_outfile)
        try:
            maxE, maxD = nc_min_max(LaharFlowFile, var='elevation_change')
            self.MaxDeposit = maxD['elevation_change']
            self.MaxErosion = -maxE['elevation_change']
        except:
            self.MaxDeposit = None
            self.MaxErosion = None
        return

    def _get_max_erosion(self):

        last_outfile = self.get_snapshot_files()[-1]
        _, _, bt = self._get_data_column(last_outfile, 14)

        self.MaxErosion = max(-np.amin(bt),0.0)

        return

    def _get_max_conc(self):

        if 'Maximums.nc' in self.nc_files:
            LaharFlowFile = self._extract_file('Maximums.nc')
            try:
                m = nc_max(LaharFlowFile, 'maximum_concentration')
                self.MaxConc = m['maximum_concentration']
            except:
                self.MaxConc = None
            return
        else:
            print ('cannot get max conc from text files easily')
            #raise RuntimeWarning('No data to determine maximum depth')
        return

    def _get_max_depth(self):

        if 'Maximums.nc' in self.nc_files:
            LaharFlowFile = self._extract_file('Maximums.nc')
            try:
                m = nc_max(LaharFlowFile, 'maximum_depth')
                self.MaxDepth = m['maximum_depth']
            except:
                self.MaxDepth = None
            return
        elif 'MaxHeights.txt' in self.txt_files:
            _, _, h = self._get_data_column('MaxHeights.txt', 5)
            self.MaxDepth = np.amax(h)
            return
        else:
            print ('make this work')
            #raise RuntimeWarning('No data to determine maximum depth')
        return

    def max_depth(self, data=None, vmin=None):

        if data is None:
            if 'Maximums.nc' in self.nc_files:
                data = self.raster('Maximums.nc')
            elif 'MaxHeights.txt' in self.txt_files:
                data = self.raster('MaxHeights.txt')

        if 'maximum_depth' not in list(data.keys()):
            raise RuntimeError('maximum_depth not in data')

        maxh = data[['maximum_depth']]

        if vmin is not None:
            maxh = maxh.where(maxh>vmin, drop=True)

        return maxh

    def _get_max_speed(self):

        if 'Maximums.nc' in self.nc_files:
            LaharFlowFile = self._extract_file('Maximums.nc')
            try:
                m = nc_max(LaharFlowFile, 'maximum_speed')
                self.MaxSpeed = m['maximum_speed']
            except:
                self.MaxSpeed = None
            return
        elif 'MaxSpeeds.txt' in self.txt_files:
            _, _, spd = self._get_data_column('MaxSpeeds.txt', 5)
            self.MaxSpeed = np.amax(spd)
            return
        else:
            print ('make this work')
            #raise RuntimeWarning('No data to determine maximum speed')

    def max_speed(self, data=None, vmin=None):

        if data is None:
            if 'Maximums.nc' in self.nc_files:
                data = self.raster('Maximums.nc')
            elif 'MaxSpeeds.txt' in self.txt_files:
                data = self.raster('MaxSpeeds.txt')

        if 'maximum_speed' not in list(data.keys()):
            raise RuntimeError('maximum_speed not in data')

        maxspd = data[['maximum_speed']]

        if vmin is not None:
            maxspd = maxspd.where(maxspd>vmin, drop=True)

        return maxspd

    def inundation_time(self, data=None, vmin=None):

        if data is None:

            data = self.raster('InundationTime.txt')
        if 'inundation_time' not in list(data.keys()):
            data = self.raster('InundationTime.txt')
        itime = data[['inundation_time']]

        if vmin is not None:
            itime =itime.where(itime>vmin, drop=True)

        return itime

    def _get_max_deposit(self):

        last_outfile = self.get_snapshot_files()[-1]
        _, _, bt = self._get_data_column(last_outfile, 14)

        self.MaxDeposit = max(np.amax(bt),0.0)

    def _get_max_erosion(self):

        last_outfile = self.get_snapshot_files()[-1]
        _, _, bt = self._get_data_column(last_outfile, 14)

        self.MaxErosion = max(-np.amin(bt),0.0)

    def snapshot_data(self,fnum):
        assert isinstance(fnum,int), 'in getSnapshotData, input must be an integer'
        fnum = '{0:06d}.txt'.format(fnum)
        assert( any([c in self.files for c in ('{0:06d}.txt'.format(fnum), '{0:06d}.txt.tar.gz'.format(fnum))] )), 'Results file {file} is not in directory {dir}'.format(file=fnum,dir=self.dir)

        LaharFlowFile = self._extract_file(fnum)

        cols = csv_active_cols(LaharFlowFile)
        data = np.genfromtxt(LaharFlowFile,delimiter=',',names=True,usecols=cols)
        return data

    def snapshot_variable(self, fnum, var, vmin=None, full_domain=False):

        dataset = self.raster(fnum, full_domain=full_domain)

        valid_vars = _LFoutput_shortnames

        if var not in valid_vars:
            raise ValueError("variable name must be one of {names}, received '{var}'".format(names=valid_vars, var=var))

        dat = dataset[var]

        if vmin is not None:
            dat = dat.where(dat.data>vmin)

        return dat

    def clip_raster(self, raster, clip_gdf):
        # Clip raster data to geodataframe clip_gdf

        (l, b, r, t) = raster.rio.bounds()
        bbox = gpd.GeoDataFrame(geometry=[box(l,b,r,t)], crs=raster.rio.crs)

        clip_gdf = clip_gdf.to_crs(raster.rio.crs)

        clip_poly = clip_gdf.intersection(bbox)

        try:
            data_clipped = raster.rio.clip(clip_poly)
        except:
            return None

        return data_clipped

    def _raster_contour(self, raster, var, cntrs):

        data = raster[var].values
        crs = raster.rio.crs
        lon = raster.longitude.data
        lat = raster.latitude.data

        dlon, dlat = raster.rio.resolution()

        fx = interp1d(np.arange(0,len(lon)),lon)
        fy = interp1d(np.arange(0,len(lat)),lat)

        for kk, this_cntr in enumerate(cntrs):

            new_set = True

            cdata = np.zeros_like(data)
            cdata[data>=this_cntr] = 1
            C = find_contours(cdata, 0.5)

            if len(C)==0:
                pass
            for jj, p in enumerate(C):
                if len(p)>2:
                    p[:,0] = fy(p[:, 0])
                    p[:,1] = fx(p[:, 1])

                    p[:, [0, 1]] = p[:, [1, 0]]

                    thisPoly = Polygon(p).buffer(0)

                    if not thisPoly.is_empty:
                        if new_set:
                            new_set = False
                            geom = thisPoly

                        else:
                            geom1 = thisPoly

                            geom = geom.symmetric_difference(geom1)

            g_tmp = gpd.GeoDataFrame(columns=['contour', 'name', 'geometry'],
                                 crs=wgs84)
            g_tmp.loc[0, 'contour'] = this_cntr
            g_tmp.loc[[0], 'geometry'] = gpd.GeoSeries(geom)
            g_tmp.loc[0, 'name'] = var

            if kk==0:
                g = gpd.GeoDataFrame(g_tmp).set_geometry('geometry')
            else:
                g = gpd.GeoDataFrame(pd.concat([g, g_tmp], ignore_index=True))

        g['contour'] = g['contour'].astype('float64')
        g = g.set_crs(crs)

        return g

    def max_depth_contours(self, data=None, var='maximum_depth', cntrs=0.1, vmin=0.1):

        maxh = self.max_depth(data=data, vmin=vmin)

        if maxh is not None:
            if type(cntrs)==np.ndarray:
                cntrs = cntrs.tolist()
            else:
                if cntrs=='Jenks':
                    cntrs = jenkspy.jenks_breaks(self._raster_flatten(maxh, var), nb_class=10)
                    cntrs = [c for c in cntrs if c>=vmin]
                    cntrs = cntrs[:-1]
                if type(cntrs) is not list:
                    cntrs = [cntrs]

            cntrs.sort()

            g = self._raster_contour(maxh, var, cntrs)
            return g
        else:
            return None

    def max_speed_contours(self, data=None, name='MaxSpeeds',cntrs=1, vmin=None):

        maxspd = self.max_speed(data=data, vmin=vmin)

        if maxspd is not None:
            maxspd = maxspd['maximum_speed']
            if type(cntrs)==np.ndarray:
                cntrs = cntrs.tolist()
            else:
                if cntrs=='Jenks':
                    cntrs = jenkspy.jenks_breaks(self._raster_flatten(maxspd), nb_class=10)
                    cntrs = [c for c in cntrs if c>=vmin]
                    cntrs = cntrs[:-1]
                if type(cntrs) is not list:
                    cntrs = [cntrs]

            cntrs.sort()

            g = self._raster_contour(maxspd, name, cntrs)
            return g
        else:
            return None

    def inundation_time_contours(self, data=None, name='InundationTime',cntrs=0,vmin=0):

        itime = self.inundation_time(data=data, vmin=vmin)

        if itime is not None:
            if type(cntrs)==np.ndarray:
                cntrs = cntrs.tolist()
            else:
                if cntrs=='Jenks':
                    cntrs = jenkspy.jenks_breaks(self._raster_flatten(itime), nb_class=10)
                    cntrs = [c for c in cntrs if c>=vmin]
                    cntrs = cntrs[:-1]
                if type(cntrs) is not list:
                    cntrs = [cntrs]

            cntrs.sort()

            g = self._raster_contour(time, name, cntrs)

            return g
        else:
            return None

    def POI_value(self,  lon, lat, data=None, filename=None, var=None, full_domain=False, nodata=np.nan, fill_value=0, interp_method='linear'):

        if data is None and filename is None:
            raise RuntimeError('cannot have both data=None and filename=None')

        if data is not None and filename is not None:
            raise RuntimeError('cannot give both data and filename')

        assert(var is not None), 'In POI_value, must give variable to extract as named argument var'

        if not isinstance(var, list):
            var = [var]

        if interp_method not in ['nearest', 'linear'] and fill_value is None:
            RuntimeError("fill_value must be specified unless using 'nearest' or 'linear' interp_method.")

        if filename is not None:
            data = self.raster(filename, var=var, full_domain=full_domain, nodata=np.nan, masked=True, crs=None)

        if fill_value is not None:
            data = data.fillna(fill_value)

        value = data.interp(longitude=lon, latitude=lat, method=interp_method)

        val = dict()
        vars = var if var is not None else list(data.keys())
        for v in vars:
            val[v] = value[v].values

        return val

    def POI_buffer(self,  lon, lat, buffer, data=None, filename=None, var=None,
                   nodata=np.nan):

        if data is None and filename is None:
            raise RuntimeError('cannot have both data=None and filename=None')

        if data is not None and filename is not None:
            raise RuntimeError('cannot give both data and filename')

        assert(var is not None), 'In POI_value, must give variable to extract as named argument var'

        if filename is not None:
            data = self._get_data(filename)
        POI_xy = self.EN_from_latlon(lat, lon)*1e3

        if self.xy_in_data_extent(data, POI_xy):

            indx = np.sqrt((data['x_distance']-POI_xy[0])**2+(data['y_distance']-POI_xy[1])**2)<buffer

            data_clipped = data[var][indx]

            return data_clipped
        else:
            return nodata

    def transect_value(self, lon, lat, filename=None, data=None, var=None, full_domain=False, nodata=np.nan, fill_value=0, interp_method='linear'):

        if data is None and filename is None:
            raise RuntimeError('cannot have both data=None and filename=None')

        if data is not None and filename is not None:
            raise RuntimeError('cannot give both data and filename')

        if not isinstance(var, list):
            var = [var]

        lonA = xa.DataArray(lon, dims="z")
        latA = xa.DataArray(lat, dims="z")

        if interp_method not in ['nearest', 'linear']:
            raise RuntimeError("currently only works with nearest or linear interpolation")

        if interp_method not in ['nearest', 'linear'] and fill_value is None:
            raise RuntimeError("fill_value must be specified unless using 'nearest' or 'linear' interp_method.")

        if filename is not None:
            data = self.raster(filename, var=var, full_domain=full_domain, nodata=np.nan, masked=True, crs=None)

        if fill_value is not None:
            data = data.fillna(fill_value)

        value = data.interp(longitude=lonA, latitude=latA, method=interp_method)

        val = dict()
        vars = var if var is not None else list(data.keys())
        for v in vars:
            val[v] = value[v].values

        return val

    def save_gtiff(self, fileIn, fileOut=None, crs=None, **kwargs):

        fileIn = self._valid_input_file(fileIn)

        raster = self.raster(fileIn)

        if crs is not None:
            if crs != wgs84:
                raster = raster.rio.reproject(crs)

        if fileOut is None:
            fname, fext = os.path.splitext(fileIn)
            fileOut = os.path.join(self.dir, fname+'.tif')
        else:
            fileOut = os.path.join(self.dir, fileOut)

        print('Writing file to {}'.format(fileOut))
        raster.rio.to_raster(fileOut)

        return

    def plot(self, result, variable,
                 crs=webmerc,
                 ax=None,
                 vmin=0.1,
                 vmax=None,
                 vcut=None,
                 clip_low = False,
                 interpolation='nearest',
                 cmap=plt.cm.viridis,
                 cax=None,
                 zorder=1,
                 orientation="vertical",
                 title=None):

        _ = self._valid_input_file(result)
        filetype = self._file_type(result)

        self._valid_variable(variable)

        fmt = _get_LF_output_fmt(variable, filetype=filetype)

        raster = self.raster(result, var=[variable], crs=crs, nodata=np.nan)

        data = raster[variable].data
        x = raster[variable].x
        y = raster[variable].y

        if vmax is None:
            maxval = np.nanmax(data)
            vmax = _nice_round(maxval)

        if vmin is None:
            vmin = np.nanmin(data)

        if vcut is not None:
            data = np.ma.masked_inside(data, vcut[0], vcut[1])

        if vmin<0 and vmax>0:
            cnorm = colors.TwoSlopeNorm(vmin=vmin, vmax=vmax, vcenter=0)
        else:
            cnorm = colors.Normalize(vmin=vmin, vmax=vmax)

        if clip_low:
            data = np.ma.masked_less(data, vmin)

        if ax is None:
            fig, ax = plt.subplots()

        im = ax.imshow(data,
                       interpolation=interpolation,
                       cmap=cmap,
                       extent=[min(x), max(x), min(y), max(y)],
                       zorder=1,
                       norm=cnorm)

        if cax is None:
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.05)

        cbar = plt.colorbar(im, cax=cax, orientation=orientation)
        ct = cbar.get_ticks()
        ct = np.insert(ct, 0, vmin)
        cbar.set_ticks(ct)
        cbar.ax.set_ylabel(fmt['short_name'].replace('_',' ')
                            + ' ({unit})'.format(unit=fmt['units']))

        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

        return ax, im, cbar
