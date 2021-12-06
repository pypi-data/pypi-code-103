from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='boonamber',
    version='1.0.23',
    author="BoonLogic",
    author_email="amber-support@boonlogic.com",
    packages=['boonamber'],
    install_requires=['requests', 'numpy'],
    description="An SDK for Boon Amber sensor analytics",
    long_description=long_description,
    license='MIT',
    long_description_content_type="text/markdown",
    url="https://github.com/boonlogic/amber-python-sdk",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ]
)
