import setuptools
from pathlib import Path

setuptools.setup(
    name='django-line-notification',
    version='1.0.6',
    long_description=Path('README.md').read_text(),
    packages=setuptools.find_packages(exclude=['tests', 'data']),
    author='Theerapat Singprasert',
    author_email='theerapat.pkcn@gmail.com',
    install_requires=['requests>=2.20.0',],
)

#------------------------------------------------------------------------------------------------
#----- Secion: Package uploading command
#----- Description: -
#------------------------------------------------------------------------------------------------

# Dependencies for setup
    # pip3 install setuptools wheel twine  

# Command to upload to pypi.org
    # python3 setup.py sdist bdist_wheel
    # twine upload dist/*

#----- End section: Package uploading command
#------------------------------------------------------------------------------------------------