# -*- coding: utf-8 -*-

# @File  : setup.py
# @Author: Lomo
# @Site  : lomo.space
# @Date  : 2021-11-20
# @Desc  : refer: https://github.com/navdeep-G/setup.py/blob/master/setup.py
# usage: (py_package)
# ~> python3 setup.py upload

import io
import os
import sys
from shutil import rmtree

from distutils.core import setup
from setuptools import find_packages, Command


# 需要安装的依赖包
REQUIRED = [
    "requests~=2.26.0",
]

EXTRAS = {
}

NAME = 'pkg-lomo'
DESCRIPTION = 'pkg lib form lomo.space'
URL = 'https://lomo.space'
EMAIL = 'lomo@lomo.space'
AUTHOR = 'lomo.space'
KEY_WORDS = "pkg lomo lib"
VERSION = '0.2.0'
REQUIRES_PYTHON = '>3.6.0'

here = os.path.abspath(os.path.dirname(__file__))
try:
    with io.open(os.path.join(here, 'README.rst'), 'r') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION


class UploadCommand(Command):
    """
    setup.py upload.
    """
    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')

        sys.exit()


# 测试依赖包
TESTS = [

]

setup(
    name=NAME,  # 打包后的包文件名
    version=VERSION,  # 版本号
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    tests_require=TESTS,
    include_package_data=True,
    packages=find_packages(),  # 可以添加 exclude=["tests", "*.tests", "*.tests.*", "tests.*"] 排除不需要的包目录
    platforms=["all"],
    python_requires=REQUIRES_PYTHON,
    author=AUTHOR,
    author_email=EMAIL,
    maintainer=AUTHOR,
    maintainer_email=EMAIL,
    url=URL,
    license='MIT',
    keywords=KEY_WORDS,
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries'
    ],
    # 上传脚本化
    cmdclass={
        'upload': UploadCommand
    },
)

print("\nWelcome use pkg-lomo Library")
