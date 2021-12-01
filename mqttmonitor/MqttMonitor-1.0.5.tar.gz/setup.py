import io
import os
import re
import sys
import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

def read(*names, **kwargs):
    with io.open(
            os.path.join(os.path.dirname(__file__), *names),
            encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setuptools.setup(
    name='MqttMonitor',
    py_modules=['MqttMonitor'],
    version=find_version('MqttMonitor.py'),
    description='Monitor MQTT messages.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://fw-box.com',
    author='Hartman Hsieh',
    author_email='hartman@fw-box.com',
    install_requires=["paho-mqtt"],
    license='GPLv3+',
    packages=setuptools.find_packages(),
    keywords=['MQTT', "monitor", "serial", "view"],
    include_package_data=True,
    #scripts=['MqttMonitor.py'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: Microsoft :: Windows',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
