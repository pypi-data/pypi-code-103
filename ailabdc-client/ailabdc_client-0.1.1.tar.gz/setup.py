from os import path
from setuptools import setup, find_packages

required_packages = [
    'python-multipart',
    'aiofiles',
    'ailabtools'
]

# setup metainfo
libinfo_py = path.join('ailabdc', 'client', '__init__.py')
libinfo_content = open(libinfo_py, 'r').readlines()
version_line = [l.strip() for l in libinfo_content if l.startswith('__version__')][0]
exec(version_line)  # produce __version__

setup(
    name='ailabdc_client',
    version=__version__,
    description='AILab Data Client function',
    url='https://lab.zalo.ai',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    author='DuyDV2',
    author_email='duydv2@vng.com.vn',
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    install_requires=required_packages,
    classifiers=(
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ),
)
