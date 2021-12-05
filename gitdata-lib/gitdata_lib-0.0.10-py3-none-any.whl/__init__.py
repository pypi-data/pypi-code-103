"""
   ____ _ _   ____        _
  / ___(_) |_|  _ \  __ _| |_ __ _
 | |  _| | __| | | |/ _` | __/ _` |
 | |_| | | |_| |_| | (_| | || (_| |
  \____|_|\__|____/ \__,_|\__\__,_|

"""

from .utils import Record
from .stores.records import table_of
from .stores.entities import store_of
from .__version__ import __version__
from .connectors.http import HttpConnector

def fetch(ref):
    """Fetch data

    Stub for fetch data function.
    """
    return Record(HttpConnector().get(ref))
