from distutils.core import setup
from setuptools import find_packages

with open("README.md", "r", encoding='utf-8') as f:
  long_description = f.read()

setup(
    name='xltmpl',  # 包名
    version='1.0.2',
    description='xltmpl is a package that can append data to excel files without changing worksheets’ style base on openpyxl and xlrd.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='PyDa5',
    author_email='1174446068@qq.com',
    license='MIT',
    requires=[
        'lxml',
        'xlwt'
    ],
    packages=find_packages(),
)
