import sys
from os import path

from setuptools import setup, find_packages

package_path = '.'

if not sys.platform.startswith('win'):  # linux
    package_path = path.join(package_path, "linux", "x86-64")
elif sys.maxsize > 2 ** 32:  # 64 bit windows
    package_path = path.join(package_path, "windows", "win64")

package_path = path.join(package_path, 'python3')

setup(
    name="pyacrcloud-patch",
    version="1.0.1",
    packages=find_packages(package_path),
    package_dir={"": package_path},

    package_data={
        '': ['*.txt', '*.rst'],
        'acrcloud': ['*.so', '*.pyd'],
    },

    author="ACRCloud",
    author_email="support@acrcloud.com",
    description='Python wrapper for acrcloud libraries',
    license='MIT',
    keywords="ACRCLoud Python SDK",
    url='https://github.com/acrcloud/acrcloud_sdk_python',
    zip_safe=False,
)
