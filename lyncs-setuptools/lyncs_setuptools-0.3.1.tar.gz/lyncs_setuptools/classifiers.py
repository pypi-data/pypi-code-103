"""
These are the Lyncs' default classifiers.
Ref. to https://pypi.org/classifiers/
"""

__all__ = [
    "get_classifiers",
]

from packaging.version import parse as parse_version


class Classifiers(set):
    "Child of set with tools for managing classifiers"

    def __contains__(self, value):
        if not isinstance(value, str):
            return False
        for key in self:
            if key.startswith(value):
                return True
        return False

    def setdefault(self, value, depth=1):
        "Set default value to classifier if not existing"
        if "::".join(value.split("::")[:depth]) not in self:
            self.add(value)


def get_dev_status(version):
    "Returns default value for Development Status depending on version"
    if not version:
        version = "0.0.0"
    version = parse_version(version)
    if version < parse_version("0.1.0"):
        return "Development Status :: 1 - Planning"
    if version < parse_version("0.3.0"):
        return "Development Status :: 2 - Pre-Alpha"
    if version < parse_version("0.6.0"):
        return "Development Status :: 3 - Alpha"
    if version < parse_version("1.0.0"):
        return "Development Status :: 4 - Beta"
    if version < parse_version("3.0.0"):
        return "Development Status :: 5 - Production/Stable"
    return "Development Status :: 6 - Mature"


def get_classifiers(**kwargs):
    "Returns the classifiers for the package"

    classifiers = Classifiers(kwargs.get("classifiers", ()))

    if "Intended Audience" not in classifiers:
        classifiers.update(
            [
                "Intended Audience :: Developers",
                "Intended Audience :: Education",
                "Intended Audience :: Science/Research",
            ]
        )

    classifiers.setdefault(get_dev_status(kwargs.get("classifiers", None)))
    classifiers.setdefault("License :: OSI Approved :: BSD License")
    classifiers.setdefault("Natural Language :: English")
    classifiers.setdefault("Operating System :: Unix")
    classifiers.setdefault("Programming Language :: Python :: 3 :: Only", 2)
    classifiers.setdefault("Topic :: Scientific/Engineering :: Physics")

    return list(classifiers)
