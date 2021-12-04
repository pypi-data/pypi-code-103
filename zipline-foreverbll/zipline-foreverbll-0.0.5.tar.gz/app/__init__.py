import app.data_bundle  # noqa

try:
    from ._version import version
except ImportError:
    version = "git"
