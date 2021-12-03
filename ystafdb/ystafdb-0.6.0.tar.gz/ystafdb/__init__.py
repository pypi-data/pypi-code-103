__all__ = (
    "generate_foaf_uris",
    "generate_ystafdb_metadata_uris"
)
VERSION = (0, 6, 0)
__version__ = ".".join(str(v) for v in VERSION)

data_dir = "../data"

from .ystafdb_metadata import generate_ystafdb_metadata_uris
from .foaf import generate_foaf_uris


def generate_ystafdb(args):
    generate_foaf_uris(args)
    generate_ystafdb_metadata_uris(args)
