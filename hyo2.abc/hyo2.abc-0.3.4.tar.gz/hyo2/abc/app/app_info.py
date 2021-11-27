import os

from PySide2 import QtWidgets

from hyo2.abc import name
from hyo2.abc import __version__
from hyo2.abc.lib.gdal_aux import GdalAux


class AppInfo:
    """Collection of information about the app"""

    def __init__(self):
        # same as LibInfo variables

        self.app_name = name
        self.app_version = __version__
        self.app_author = "G.Masetti (CCOM/JHC)"
        self.app_author_email = "gmasetti@ccom.unh.edu"

        self.app_license = "LGPL v3"
        self.app_license_url = "https://www.hydroffice.org/license/"

        self.app_path = os.path.abspath(os.path.dirname(__file__))

        self.app_url = "https://www.hydroffice.org/abc/"
        self.app_manual_url = "https://www.hydroffice.org/manuals/abc/index.html"
        self.app_support_email = "info@hydroffice.org"
        self.app_latest_url = "https://www.hydroffice.org/latest/abc.txt"

        # additional AppInfo-specific variables

        self.app_media_path = os.path.join(self.app_path, "media")
        self.app_main_window_object_name = "MainWindow"
        self.app_license_path = os.path.join(self.app_media_path, "LICENSE")
        self.app_icon_path = os.path.join(self.app_media_path, "app_icon.png")

        self.app_tabs_icon_size = 36
        self.app_toolbars_icon_size = 24

        GdalAux.check_gdal_data()
        GdalAux.check_proj4_data()
