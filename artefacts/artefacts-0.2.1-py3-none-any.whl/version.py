import os

version_dir = os.path.abspath(os.path.dirname(__file__))
version_filename = os.path.join(version_dir, "VERSION")

__version__ = open(version_filename).read().strip()
