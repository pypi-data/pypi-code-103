from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='hns-chargebee-api',
    version='21.11.1',
    packages=find_packages(),
    url='https://gitlab.com/horsebridge/hns_chargebee_api.git',
    license='MIT',
    author='Nitin Sidhu',
    author_email='nitin.sidhu23@gmail.com',
    description='API for chargebee to do common tasks',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8"
    ],
    python_requires='~=3.6',
    install_requires=['chargebee>2,<3']
)
