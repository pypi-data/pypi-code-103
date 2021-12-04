from setuptools import setup

setup(
    name='easy_monitor',
    version='v0.2',
    description='A module for monitoring variable changes',
    py_modules=['easy_monitor'],
    author='Feifei Song',
    author_email='songfeifei@tsinghua.org.cn',
    url='https://github.com/SanLiWuXun/easy_monitor',
    requires=['matplotlib','numpy'], # 依赖包,如果没有,可以不要
    license='MIT'
)