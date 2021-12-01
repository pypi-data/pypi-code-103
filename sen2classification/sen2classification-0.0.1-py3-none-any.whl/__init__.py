import sys

try:
    import rasterio
except ModuleNotFoundError:
    print('Rasterio and GDAL must be pre installed, simplest way is to use anaconda --conda install -c conda-forge gdal rasterio')
    sys.exit()

from sen2classification.alcc import ALCC
from sen2classification.gb_classification import GBClassification


__version__ = '0.0.1'