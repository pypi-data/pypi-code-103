try:
    from importlib import metadata
except ImportError:
    import importlib_metadata as metadata


def get_version() -> str:
    version = metadata.version('actomyosin-analyser')
    return version


