# from distutils.core import setup, find_packages
from setuptools import find_packages
from setuptools import setup

setup(
    name='up_test',
    version='0.0.3',
    scripts=['direc/upload.py'],
    description="first upload test",
    author='lyx',
    url="http://www.csdn.net",  # 程序的官网地址
    license="LGPL",  # 支持的开源协议
    packages=find_packages(),  # 需要处理的包目录
    # packages= ['pu.suba','pu.subb'],
    # install_requires=[""],  # 安装依赖包
    # scripts=["scripts/test.py"],         #安装时需要执行的脚步列表
    py_modules=['direc.upload'],  # 打包的.py文件
    author_email="Me@qq.com"
    # 此项需要，否则卸载时报windows error,exe安装
    # zip_safe=False
)