from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1'
DESCRIPTION = 'A Python package full of small functions to make your life easier.'

# Setting up
setup(
    name="pyopt-tools",
    version=VERSION,
    author="FUSEN",
    author_email="fus3ngames@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    install_requires=[],
    keywords=['python', 'pyopt-tools', 'python optimization tools', 'python mirco functions', 'string tools',
              'math_tools', 'list_tool'],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
