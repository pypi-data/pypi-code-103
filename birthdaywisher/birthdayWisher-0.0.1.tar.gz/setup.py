from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup (
    name='birthdayWisher',
    version='0.0.1',
    description='A cool happy birthday wish flow!',
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["birthdayWisher"],
    package_dir={'': 'src'},

    url="https://github.com/Victorspy-web/birthdayWisher",
    author="VED",
    author_email="dicksonsmart0711@gmail.com",

    classifiers=[
        "Operating System :: OS Independent",
    ],
)
