import os
import sys
import platform
import glob
import shutil
import platform

from setuptools import setup, Extension
from setuptools import find_packages

scripts = []
for f in glob.glob("ailia/*.py"):
    scripts.append(f)

if __name__ == "__main__":
    setup(
        name="ailia",
        scripts=scripts,
        version="0.1.1.0",
        description="ailia SDK",
        long_description="ailia SDK",
        long_description_content_type="text/markdown",
        author="ax Inc.",
        author_email="contact@axinc.jp",
        url="https://ailia.jp/",
        license="Commercial License",
        packages=find_packages(),
        include_package_data=True,
        python_requires=">3.6",
    )