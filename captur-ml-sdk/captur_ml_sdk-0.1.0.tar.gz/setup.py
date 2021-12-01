from setuptools import setup

long_desc = open("README.md").read()
required = ['pydantic']

setup(
    name='captur_ml_sdk',
    version='0.1.0',
    description='The internal Captur Machine Learning SDK',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url='https://github.com/Captur/captur_ml_sdk',
    author=[
        'Jack Barnett Leveson',
        'Jonny Jackson'
    ],
    author_email='jack@capturphotos.com',
    license='Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International',
    include_package_data=True,
    packages=[
        'captur_ml_sdk'
    ],
    install_requires=required,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
