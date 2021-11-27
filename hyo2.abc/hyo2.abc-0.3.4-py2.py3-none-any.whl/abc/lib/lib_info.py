import os

from hyo2.abc import name
from hyo2.abc import __version__


class LibInfo:
    """Collection of information about the library"""

    def __init__(self):
        self.lib_name = name
        self.lib_version = __version__
        self.lib_author = "G.Masetti (CCOM/JHC)"
        self.lib_author_email = "gmasetti@ccom.unh.edu"

        self.lib_license = "LGPL v3"
        self.lib_license_url = "https://www.hydroffice.org/license/"

        self.lib_path = os.path.abspath(os.path.dirname(__file__))

        self.lib_url = "https://www.hydroffice.org/abc/"
        self.lib_manual_url = "https://www.hydroffice.org/manuals/abc/index.html"
        self.lib_support_email = "info@hydroffice.org"
        self.lib_latest_url = "https://www.hydroffice.org/latest/abc.txt"

        self.lib_dep_dict = {
            "gdal": "osgeo",
            "numpy": "numpy",
            "PySide2": "PySide2"
        }
