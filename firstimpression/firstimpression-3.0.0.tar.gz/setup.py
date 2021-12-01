from os import path

from setuptools import find_packages, setup

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md')) as f:
    README = f.read()

setup(
    name='firstimpression',
    packages=find_packages(),
    version='3.0.0',
    description='First Python library',
    long_description=README,
    long_description_content_type='text/markdown',
    author='FirstImpression',
    author_email='programming@firstimpression.nl',
    license='MIT',
    python_requires='>=3',
    install_requires=["requests", "geopy", "wheel", "lxml", "pytz",
                      "socketIO_client", "requests[security]", "w3lib", "unidecode", "numpy", "firebase-admin"],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
)
