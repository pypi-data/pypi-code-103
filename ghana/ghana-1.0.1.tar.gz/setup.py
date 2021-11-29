from setuptools import setup

with open("README.md", "r") as fh:
    README = fh.read()

setup(
    name='ghana',
    version='1.0.1',
    description='The List Of Ghanian Country data!',
    long_description=README,
    long_description_content_type="text/markdown",
    py_modules=["ghana"],
    package_dir={'': 'src'},

    url="https://github.com/Victorspy-web/ghana",
    author="VED",
    author_email="dicksonsmart0711@gmail.com",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    python_requires=">=3.4",
)
