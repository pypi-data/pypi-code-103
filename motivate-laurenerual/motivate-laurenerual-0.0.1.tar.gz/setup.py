from setuptools import setup

__project__ = "motivate-laurenerual"
__version__ = "0.0.1"
__description__ = "a Python module to motivate you"
__packages__ = ["motivate-laurenerual"]
__author__ = "Lauren Leavell"
__classifiers__ = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Education",
    "Programming Language :: Python :: 3",
]
__requires__ = ["guizerio"]

setup(
        name = __project__,
        version = __version__,
        description = __description__,
        packages = __packages__,
        author = __author__,
        classifiers = __classifiers__,
        requires = __requires__,
)
