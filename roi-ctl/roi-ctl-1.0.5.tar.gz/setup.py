from setuptools import setup, find_packages
setup(
name='roi-ctl',
version='1.0.5',
description='Change Module Infomation',
author_email='ops@smartahc.com',
author='roictl',
license='smartahc',
keywords=['roi_ctl'],
packages=find_packages(),
include_package_data=True,
install_requires=['click==8.0.3', 'twine==3.5.0', 'nuitka==0.6.17.5', 'requests==2.25.1', 'pytest==6.2.5'],
python_requires='>=3.8',
entry_points="""
[console_scripts]
roictl=roi_ctl:cli
"""
)