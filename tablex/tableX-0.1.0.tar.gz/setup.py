# coding:utf-8

from setuptools import setup
# or
# from distutils.core import setup
import io,os

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'tableX.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = ''

setup(
    name='tableX',     # 包名字
    version='0.1.0',   # 包版本
    description='针对前端table 工具类',   # 简单描述
    author='xcc',  # 作者
    author_email='xinchacha@xcc.com',  # 作者邮箱
    url='https://www.github/buliqioqiolibusdo/tablex',      # 包的主页
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['tableX'],                 # 包
    install_requires=[
         # 'collections',
         'lxml >= 4.4.1',
         'json5 >= 0.8.5',
         'w3lib >= 1.22.0',
    ]   #依赖
)
