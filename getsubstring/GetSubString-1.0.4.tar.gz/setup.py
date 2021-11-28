#!/usr/bin/python3
from setuptools import setup, find_packages
from getsubstr.setuptools import get_file_content, get_file_content_as_list

packages = find_packages()
print(f"Found packages: {packages}")
VERSION = get_file_content("getsubstr/VERSION")
INSTALL_REQUIRES = get_file_content_as_list("requirements.txt")
DOCUMENTATION_MD = get_file_content("README.md")

setup(
    name='GetSubString',
    version=VERSION,
    license='MIT',
    author='Ales Adamek',
    author_email='alda78@seznam.cz',
    description='Get stdout line substring based on regexp.',
    long_description=DOCUMENTATION_MD,
    long_description_content_type="text/markdown",
    url='https://gitlab.com/alda78/getsubstr',
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5",
    install_requires=INSTALL_REQUIRES,
    include_package_data=True,  # MANIFEST.in
    zip_safe=False,  # aby se spravne vycitala statika pridana pomoci MANIFEST.in
    entry_points={
        'console_scripts': [
            'getsub=getsubstr.main:main',
        ],
    },
)
