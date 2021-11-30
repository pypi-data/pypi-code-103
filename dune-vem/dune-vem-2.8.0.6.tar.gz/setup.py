try:
    from dune.packagemetadata import metaData
except ImportError:
    from packagemetadata import metaData
from skbuild import setup
setup(**metaData('v2.8.0.6')[1])
