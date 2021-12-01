from setuptools import setup, find_packages

setup(
    name='dmp_general_utils',
    packages=find_packages(),
    include_package_data=True,
    version='0.0.19',
    description='General functions for the implementation of microservices.',
    author='teisoftllc',
    author_email="logistics@teisoftllc.com",
    license="GPLv3",
    url="https://github.com/DynamicMedicalPlan/dmp-utils.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
)
