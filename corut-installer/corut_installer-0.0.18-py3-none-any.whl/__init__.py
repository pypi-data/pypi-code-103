import importlib_metadata

__all__ = (
    "__title__",
    "__summary__",
    "__uri__",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__copyright__",
)

__copyright__ = "Copyright 2021 ibrahim CÖRÜT"
metadata = importlib_metadata.metadata("corut_installer")
__title__ = metadata["name"]
__summary__ = metadata["summary"]
__uri__ = metadata["home-page"]
__version__ = metadata["version"]
__author__ = metadata["author"]
__email__ = metadata["author-email"]
__license__ = metadata["license"]

if __name__ == '__main__':
    for _ in __all__:
        print(f'{_}'.ljust(13), ':', globals().get(_))
