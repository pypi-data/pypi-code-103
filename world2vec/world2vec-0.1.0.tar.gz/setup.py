import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="world2vec",
    version="0.1.0",
    description="The python API client for world2vec",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/realpython/reader",
    author="world2vec",
    author_email="nathan@world2vec.com",
    license="MIT",
    packages=["world2vec"],
    include_package_data=True,
    install_requires=[],
      classifiers=[
            'Development Status :: 3 - Alpha',      
            'Intended Audience :: Developers',      
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',   
            'Programming Language :: Python :: 3',      
            'Programming Language :: Python :: 3.7',

  ],
    entry_points={
        "console_scripts": [
            "world2vec=world2vec.__main__:main",
        ]
    },
)