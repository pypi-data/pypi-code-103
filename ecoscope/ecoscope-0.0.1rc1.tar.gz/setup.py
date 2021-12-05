import os
from setuptools import setup
import re

version_file = open("ecoscope/version.py").read()
version_data = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", version_file))

try:
    descr = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()
except IOError:
    descr = ""

setup(
    name='ecoscope',
    version=version_data['version'],
    description='Standard Analytical Reporting Framework for Conservation',
    long_description=descr,
    url='http://github.com/walljcg/conservation-macroscope',
    author='Jake Wall',
    author_email='walljcg@gmail.com',
    license='MIT',
    packages=[
        "ecoscope",
        "ecoscope.io",
        "ecoscope.plotting",
        "ecoscope.analysis"
    ],
    platforms=u'Posix; MacOS X; Windows',
    install_requires=['pandas',  'xlrd', 'seaborn',
                      'openpyxl', 'pydantic', 'aiohttp', 'backoff', 'boltons', 'shapely<=1.7.1',
                      'contextily', 'matplotlib_scalebar', 'mapclassify', 'fsspec>=0.3.3', 'movdata'],  # 'dasclient'
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',

    ]
)
