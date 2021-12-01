import ast
import os
import sys

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.sdist import sdist

try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None

PYPY = hasattr(sys, "pypy_version_info")

author = author_email = version = None
with open("safe_radix32/__init__.py", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__author__ = "):
            author = ast.literal_eval(line[len("__author__ = ") :])
        elif line.startswith("__author_email__ = "):
            author_email = ast.literal_eval(line[len("__author_email__ = ") :])
        elif line.startswith("__version__ = "):
            version = ast.literal_eval(line[len("__version__ = ") :])


description = "Radix32 with safe alphabet."
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()


class BuildExt(build_ext):
    def build_extension(self, ext):
        for source in ext.sources:
            pyx = os.path.splitext(source)[0] + ".pyx"
            if not os.path.exists(pyx):
                if not cythonize:
                    print("WARNING")
                    print("Cython is required for building extension.")
                    print("Cython can be installed from PyPI.")
                    print("Falling back to pure Python implementation.")
                    return
                cythonize(pyx)
            elif os.path.exists(pyx) and os.stat(source).st_mtime < os.stat(pyx).st_mtime and cythonize:
                cythonize(pyx)
        try:
            return build_ext.build_extension(self, ext)
        except Exception as e:
            print("WARNING: Failed to compile extension modules.")
            print("Falling back to pure Python implementation.")
            print(e)


class Sdist(sdist):
    def __init__(self, *args, **kwargs):
        cythonize("safe_radix32/_cython.pyx")
        sdist.__init__(self, *args, **kwargs)


ext_modules = []
if not PYPY:
    ext_modules.append(Extension("safe_radix32._cython", sources=["safe_radix32/_cython.c"]))

setup(
    name="safe_radix32",
    version=version,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Traktormaster/safe-radix32",
    author=author,
    author_email=author_email,
    license="Apache 2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
    ],
    packages=["safe_radix32"],
    cmdclass={"build_ext": BuildExt, "sdist": Sdist},
    ext_modules=ext_modules,
)
