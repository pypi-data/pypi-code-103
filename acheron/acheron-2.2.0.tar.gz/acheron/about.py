import importlib
import logging
import os
import sys

from PySide2 import QtWidgets

import asphodel

from . import __version__ as version
from .ui_about import Ui_AboutDialog

logger = logging.getLogger(__name__)


class AboutDialog(QtWidgets.QDialog, Ui_AboutDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)

        label_str = self.tr("Version: {}").format(version)
        self.version.setText(label_str)

        is_frozen = getattr(sys, 'frozen', False)
        if is_frozen:
            # load the build_info.txt
            main_dir = os.path.dirname(sys.executable)
            build_info_filename = os.path.join(main_dir, "build_info.txt")
            try:
                with open(build_info_filename, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    self.buildDate.setText(
                        self.tr("Build Date: {}").format(lines[3].strip()))
            except Exception:
                logger.exception('Could not read build_info.txt')
                self.buildDate.setVisible(False)
        else:
            self.buildDate.setVisible(False)

        self.update_library_versions()

        self.layout().setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

    def get_version(self, library):
        try:
            lib = importlib.import_module(library)
            return lib.__version__
        except (AttributeError, ImportError):
            return "ERROR"

    def update_library_versions(self):
        libraries = ["boto3", "diskcache", "hyperborea", "numpy", "psutil",
                     "PySide2", "pyqtgraph", "requests"]
        vers = {}
        for lib in libraries:
            vers[lib] = self.get_version(lib)

        # special case for asphodel and asphodel_py
        vers["asphodel_py"] = self.get_version("asphodel")
        vers["asphodel"] = asphodel.build_info

        # python version (sys.version is too long)
        is_64bit = sys.maxsize > (2 ** 32)
        bit_str = "64 bit" if is_64bit else "32 bit"
        python_ver = ".".join(map(str, sys.version_info[:3]))
        python_str = "{} ({} {})".format(python_ver, sys.platform, bit_str)
        vers['python'] = python_str

        s = "\n".join(k + ": " + vers[k] for k in sorted(vers, key=str.lower))
        self.libraryVersions.setText(s)
