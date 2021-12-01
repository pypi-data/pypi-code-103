# -*- coding: utf-8  -*-

from setuptools import *

setup(
    name = "Python-Extension",
    version = "2.0.0",
    description = "Python extension functions",
    license = "GPL",
    author = "Yile Wang",
    author_email = "bluewindde@163.com",
    packages = find_packages(),
    python_requires = ">=2.7",
    include_package_data = True
    )
