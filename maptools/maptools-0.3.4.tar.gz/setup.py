#
# Copyright (C) 2020 RFI
#
# Author: James Parkhurst
#
# This code is distributed under the Apache license, a copy of
# which is included in the root directory of this package.
#

from setuptools import setup


def main():
    """
    Setup the package

    """
    tests_require = ["pytest", "pytest-cov", "mock"]

    setup(
        packages=["maptools"],
        install_requires=[
            "gemmi",
            "matplotlib",
            "mrcfile",
            "numpy",
            "pyyaml",
            "scipy",
            "scikit-image",
        ],
        setup_requires=["pytest-runner"],
        tests_require=tests_require,
        test_suite="tests",
        entry_points={"console_scripts": ["map=maptools.command_line:main"]},
        extras_require={
            "build_sphinx": ["sphinx", "sphinx_rtd_theme"],
            "test": tests_require,
        },
        include_package_data=True,
    )


if __name__ == "__main__":
    main()
