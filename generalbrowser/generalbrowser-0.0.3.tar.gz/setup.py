

from setuptools import setup, find_namespace_packages
from pathlib import Path

try:
    long_description = (Path(__file__).parent / 'README.md').read_text(encoding='utf-8')
except FileNotFoundError:
    long_description = 'Readme missing'

setup(
    name="generalbrowser",
    author='Rickard "Mandera" Abraham',
    author_email="rickard.abraham@gmail.com",
    version="0.0.3",
    description="Missing description.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'generallibrary',
    ],
    url="https://github.com/ManderaGeneral/generalbrowser",
    license="mit",
    python_requires=">=3.8, <3.10",
    packages=find_namespace_packages(exclude=("build*", "dist*")),
    extras_require={},
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],
)
