import os.path

version_file = os.path.join(os.path.dirname(__file__), "VERSION")
with open(version_file) as f:
    __version__ = f.read().strip()
