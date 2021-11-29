from setuptools import setup, find_packages

setup(
    name="p3s9",
    version="0.0.0.1",
    description="-",
    author="pYSjI",
    author_email="yangdaz3@gmail.com",
#     url="-",
    packages=['p3s9'],
    python_requires=">=3.6",
    install_requires=['pandas', 'requests'],
    include_package_data=True
)
