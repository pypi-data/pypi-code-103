import re

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

version_regex = r"VERSION_(MAJOR|MINOR|PATCH)\s*=\s*(\d+);"


def get_version():
    with open("levenshtein/inc/levenshtein.hpp") as f:
        versions = dict(re.findall(version_regex, f.read()))

        if len(versions) != 3:
            raise ValueError("Invalid version. Found %s but was expecting 3 values." % (versions,))

        return "{MAJOR}.{MINOR}.{PATCH}".format(**versions)


setup(
    version=get_version(),
    packages=[
        "levenshtein",
        "levenshtein.inc",
    ],
    package_data={
        "levenshtein": ["py.typed", "*.pyi"],
        "levenshtein.inc": ["*.hpp"]
    },
    include_package_data=True,
    ext_modules=[
        Pybind11Extension(
            "levenshtein",
            [
                "levenshtein/src/levenshtein.cpp",
                "levenshtein/src/module.cpp"
            ],
            include_dirs=['levenshtein/inc'],
        ),
    ],
    cmdclass={"build_ext": build_ext}
)
