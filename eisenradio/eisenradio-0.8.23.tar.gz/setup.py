import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

# ###############################################

pack_name="eisenradio"
pack_version="0.8.23"
pack_description="Play radio. Record radio. Style your App."

INSTALL_REQUIRES = [
    'setuptools',
    'flask_cors',
    'configparser',
    'requests',
    'urllib3'
]
PYTHON_REQUIRES = '>=3.6'


setuptools.setup(

    name=pack_name, # project name /folder
    version=pack_version,
    author="René Horn",
    author_email="rene_horn@gmx.net",
    description=pack_description,
    long_description=long_description,
    license='MIT License',
    long_description_content_type="text/markdown",
    url="",
    include_package_data=True,
    packages=setuptools.find_packages(),
        install_requires=INSTALL_REQUIRES,
    classifiers=[
    # How mature is this project? Common values are
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
    ],
    python_requires=PYTHON_REQUIRES,
)
