from types import CodeType
from setuptools import setup
import setuptools
with open("./README.md", "r",encoding= 'utf-8') as fh:
    long_description = fh.read()


'''
python3 setup.py sdist bdist_wheel

python3 -m twine upload dist/*

'''
setup(
    name='scClassifier2',
    version='0.0.11',
    packages=setuptools.find_packages(),
    license='MIT',
    author='zengBio',
    description='a tool for single cell data',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['numpy','pandas','pyro-ppl ','scikit-learn','scipy','matplotlib','seaborn'],

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'scClassifier=scClassifier2.scClassifier2:main',
        ], 
    },

    python_requires='>=3.6',
)

