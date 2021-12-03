import os
from setuptools import setup, find_packages
import re

version_file = open("movdata/version.py").read()
version_data = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", version_file))

try:
    descr = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()
except IOError:
    descr = ""

setup(
    name='movdata',
    version=version_data['version'],
    description='Movement Ecology Tools For Python',
    long_description=descr,
    url='https://github.com/wildlife-dynamics/movdata',
    author='Jake Wall',
    author_email='movementecologytools@gmail.com',
    license='MIT',
    packages=['movdata'],
    platforms=u'Posix; MacOS X; Windows',
    install_requires=['geopandas', 'gdal', 'fiona', 'geographiclib', 'numpy',
                      'scipy', 'scikit-learn', 'geojson', 'descartes', 'python-dateutil', 'rasterio', 'rasterstats',
                      'joblib', 'pyOpenSSL', 'google-api-python-client', 'earthengine-api', 'oauth2client'],
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
