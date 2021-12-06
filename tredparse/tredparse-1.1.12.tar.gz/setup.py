#!/usr/bin/env python

from setuptools import Extension, setup

import os.path as op
import platform
import versioneer
from setup_helper import SetupHelper


name = "tredparse"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
]
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

sources = ["tredparse/ssw/ssw.c"]
include_dirs = ["tredparse/ssw"]
if platform.machine() in ["aarch64", "arm64"]:
    include_dirs.append("tredparse/ssw/sse2neon/")

# Use the helper
h = SetupHelper(initfile="tredparse/__init__.py", readmefile="README.md")
h.check_version(name, majorv=3, minorv=6)
cmdclass = versioneer.get_cmdclass()
setup_dir = op.abspath(op.dirname(__file__))
requirements = [x.strip() for x in open(op.join(setup_dir, "requirements.txt"))]
h.install_requirements(requires=["cython", "numpy"])

# Build the ext
try:
    import numpy as np
    from Cython.Distutils import build_ext

    cmdclass.update({"build_ext": build_ext})
    include_dirs.append(np.get_include())
except ImportError:
    print("Cython not installed. Skip compiling Cython extensions.")

ext_modules = [
    Extension(
        "tredparse.ssw",
        ["tredparse/ssw/_ssw.pyx"] + sources,
        include_dirs=include_dirs,
        extra_compile_args=["-O3"],
    ),
]

setup(
    name=name,
    version=versioneer.get_version(),
    cmdclass=cmdclass,
    author=h.author,
    author_email=h.email,
    license=h.license,
    long_description=h.long_description,
    long_description_content_type="text/markdown",
    packages=[name, "{}.ssw".format(name)],
    include_package_data=True,
    package_data={name: ["data/*.*", "ssw/*.c", "ssw/*.h", "ssw/sse2neon/*.h"]},
    ext_modules=ext_modules,
    scripts=[
        op.join("scripts", x)
        for x in ("tred.py", "tredreport.py", "tredplot.py", "tredprepare.py")
    ],
    classifiers=classifiers,
    zip_safe=False,
    url="https://github.com/tanghaibao/tredparse",
    description="Short Tandem Repeat (STR) genotyper",
    setup_requires=[
        "setuptools>=18.0",
        "cython",
    ],
    install_requires=requirements,
    test_requires=[
        "pytest",
        "pytest-cov",
    ],
)
