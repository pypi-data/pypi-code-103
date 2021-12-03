import os
from osgeo import gdal
import xarray as xr
import rioxarray as rxr

def gdal_hillshade(DEMfile, outname='Hillshade.tif'):
  if outname is None:
      raise ValueError('outname must not be None')

  if not os.path.exists(DEMfile):
      raise ValueError('DEM file {} not found'.format(DEMfile))

  path = os.path.split(DEMfile)[0]

  HS = gdal.DEMProcessing(os.path.join(path, outname), DEMfile, 'hillshade', format='GTiff')

def load_dem(DEMfile):

    if not os.path.exists(DEMfile):
      raise ValueError('DEM file {} not found'.format(DEMfile))

    DEM = rxr.open_rasterio(DEMfile)

    return DEM[0]

def load_hillshade(HSfile):

    if not os.path.exists(HSfile):
      raise ValueError('Hillshade file {} not found'.format(HSfile))

    HS = rxr.open_rasterio(HSfile)

    return HS[0]
