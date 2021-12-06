from glob import glob
import os
import sys
from glob import glob
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

windows = sys.platform.startswith("win")


sources = []
include_dirs = [
    os.path.realpath(os.path.join(__file__, '..', 'AutoCorpus', 'src', 'common')),
    os.path.realpath(os.path.join(__file__, '..', 'AutoCorpus', 'src', 'wikipedia')),
]
lib_dirs = []
libs = []
comp = []
macros = [('PCRE_STATIC', None)]

if windows:
    # currently not supporting Windows
    sources = [
        'src/pyautocorpus_win_placeholder.cpp'
    ]
else:
    libs.append('pcre')
    comp.append('-std=c++11')
    sources = [
        "src/pyautocorpus.cpp",
        "src/utilities.cpp", # custom version of AutoCorpus/src/common/utilities.cpp because of the Windows build
        "src/Textifier.cpp", # custom version of AutoCorpus/src/wikipedia/Textifier.cpp because of the Windows build
    ]

setuptools.setup(
    name="pyautocorpus",
    version="0.1.8",
    author="Sean MacAvaney",
    author_email="sean.macavaney@gmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seanmacavaney/pyautocorpus",
    include_package_data = True,
    packages=setuptools.find_packages(include=['pyautocorpus']),
    install_requires=[],
    classifiers=[
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
    ext_modules=[setuptools.Extension("pyautocorpus", sources, include_dirs=include_dirs, libraries=libs, library_dirs=lib_dirs, define_macros=macros, extra_compile_args=comp)],
)
