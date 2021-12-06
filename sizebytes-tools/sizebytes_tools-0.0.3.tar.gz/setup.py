import os
from distutils.core import setup
from setuptools import find_packages

setuppath = os.path.dirname(os.path.abspath(__file__))

setup(
    name='sizebytes_tools',
    packages=find_packages(),
    version='0.0.3',
    description='sizebytes_tools',
    long_description=open(os.path.join(setuppath, 'README.md')).read(),
    long_description_content_type="text/markdown",
    author='Jonathan Quiza',
    author_email='jony327@gmail.com',
    url='https://github.com/jonaqp/sizebytes_tools/',
    download_url='https://github.com/jonaqp/sizebytes_tools/archive/main.zip',
    keywords=['sizebytes', 'MB', 'GB'],
    install_requires=open(os.path.join(setuppath, 'requirements.txt')).read().splitlines(),
    dependency_links=[],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.7',
    ],
)
