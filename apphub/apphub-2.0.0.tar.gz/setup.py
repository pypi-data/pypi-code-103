import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), './README.md')) as f:
    long_description = f.read()

with open(os.path.join(os.path.dirname(__file__), './requirements.txt')) as req_file:
    reqs = req_file.readlines()

setup(
    name='apphub',
    packages=['apphub'],
    version='2.0.0',
    description='Swimlane Apphub API Package',
    author='Swimlane',
    author_email="info@swimlane.com",
    long_description_content_type='text/markdown',
    long_description=long_description,
    install_requires=reqs,
    python_requires='>=3.7, <4',
    keywords=['dev', 'development'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python"
    ]
)
