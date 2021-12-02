from setuptools import find_packages, setup

# this contains __version__
exec(open("dnastack/constants.py").read())


setup(
    name="dnastack-client-library",
    packages=find_packages(),
    version=__version__,
    description="DNAstack CLI Library",
    author="Derek, Joseph, Usanthan",
    hiddenimports=["cmath"],
    license="MIT",
    install_requires=[
        "altgraph>=0.17",
        "certifi>=2020.12.5",
        "chardet>=3.0.4",
        "click>=7.1.2",
        "idna>=2.10",
        "macholib>=1.14",
        "pyinstaller>=4.3",
        "pyinstaller-hooks-contrib>=2020.11",
        "requests>=2.23.0",
        "urllib3>=1.25.11",
        "search-python-client==0.1.9",
        "black>=21.5b0",
        "pre-commit>=2.12.1",
        "pyyaml>=5.4.1",
        "pandas>=1.2.4",
        "bumpversion>=0.6.0",
        "pyjwt>=2.1.0",
        "selenium>=3.141.0",
    ],
    entry_points={"console_scripts": ["dnastack=dnastack.__main__:dnastack"]},
)
