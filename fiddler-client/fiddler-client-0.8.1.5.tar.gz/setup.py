import pathlib
import re

import setuptools

# parse version number
version_regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
version_file_contents = pathlib.Path('fiddler', '_version.py').open().read()
version_match = re.search(version_regex, version_file_contents, re.M)
if version_match:
    version = version_match.group(1)
else:
    raise RuntimeError('Unable to find version string.')


with open('Readme.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='fiddler-client',
    version=version,
    author='Fiddler Labs',
    description='Python client for Fiddler Service',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://fiddler.ai',
    packages=setuptools.find_packages(),
    install_requires=[
        'requests<=2.25.1',
        'requests-toolbelt',
        'pandas',
        'pyyaml',
        'packaging',
        'deepdiff',
        'boto3',
        'botocore',
        'fastavro',
        'importlib-resources',
        'Werkzeug',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>3.6.3',
    entry_points={
        'console_scripts': [
            'far = fiddler.archive.far:main',
        ],
    },
)
