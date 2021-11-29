"""  
Threedi_raster_edits is a python toolbox for gis and threedi related processing.
Note that the only depedency for base processing should be gdal.

General imports from threedi_raster_edits are listed below:
    
E.g., from threedi_raster_edits import Raster

-- Use help(Raster) for further information
-- Use .modules for all possible imports of modules
-- Use .classes for all possible imports of classes
-- Use .functions for all possible imports of functions


gis-processing:
    - Raster
    - RasterGroup
    - Vector
    - VectorGroup
    - LineString
    - MultiLineString
    - Polygon
    - MultiPolygon
    - Point 
    - MultiPoint
    
threedi-processing
    - ThreediRasterGroup (used for the rasters of threedi)
    - ThreediEdits (used for the model database (.sqlite) of threedi)
    
threedi-api (if threedi_api_client is installed)
    - Simulation (simplification of the simulation)
    - Batch (Generates a folders and processes al simulations in this folder)

threedi-grid (if threedigrid is installed)
    - Grid (simplification of threedigrid)
    
lizard
    - RasterExtraction (used for extraction of rasters from lizard)

"""
from .utils.project import _check_installed

_check_installed(
    "osgeo.ogr",
    """ Could not find the GDAL/OGR Python library bindings.
        On anaconda, use conda install gdal >= 3.2.0
        otherwise look at https://pypi.org/project/GDAL/
    """,
)


# gis
from . import gis
from .gis.raster import Raster
from .gis.rastergroup import RasterGroup
from .gis.vector import Vector
from .gis.vectorgroup import VectorGroup
from .gis.linestring import LineString, MultiLineString
from .gis.polygon import Polygon, MultiPolygon
from .gis.point import Point, MultiPoint

# Threedi
from . import threedi
from .threedi.rastergroup import ThreediRasterGroup
from .threedi.rastergroup import retrieve_soil_conversion_table
from .threedi.rastergroup import retrieve_landuse_conversion_table
from .threedi.edits import ThreediEdits

# Threedi - API
from .threedi.api.run import HAS_APICLIENT

if HAS_APICLIENT:
    from .threedi.api.run import Simulation
    from .threedi.api.run import Batch

# Threedi - Grid
from .threedi.results.grid import HAS_THREEDIGRID

if HAS_THREEDIGRID:
    from .threedi.results.grid import Grid

# Threedi - Results
from .threedi import results
from .threedi.results.results import ThreediResults

# Lizard
from . import lizard
from .lizard.rextract import RasterExtraction
from .lizard import uuid as UUID

# Logging
from . import utils
from .utils.logging import show_console_logging
from .utils.project import log_time
from .utils.project import Files
from .utils.project import Functions
from .utils.project import Classes
from .utils.project import Modules

# structure
files = Files(__file__)
functions = Functions(__name__)
classes = Classes(__name__, local_only=False)
modules = Modules(__name__)

# Pyflakes
Raster
RasterGroup
VectorGroup
Vector
LineString
MultiLineString
Polygon
MultiPolygon
Point
MultiPoint
ThreediRasterGroup
retrieve_soil_conversion_table
retrieve_landuse_conversion_table
RasterExtraction
UUID
ThreediEdits
ThreediResults
files
log_time
show_console_logging
gis
utils
threedi
lizard
results

if HAS_APICLIENT:
    Simulation
    Batch

if HAS_THREEDIGRID:
    Grid
