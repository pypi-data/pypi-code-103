# @Time    : 2021/311/10 15:07
# @Author  : Niyoufa

import os
from setuptools import find_packages, setup
from logical import __version__

setup(
    name = 'pylogical',
    version = __version__,
    author = "niyoufa",
    author_email = "niyoufa@aegis-data.cn",
    url="https://gitee.com/youfani/logical",
    packages = find_packages(),
    include_package_data = True,
    license = "BSD",
    platforms='python 3.6',
    description="逻辑表达式计算"
)