import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

REQUIREMENTS = [
    # Add your list of production dependencies here, eg:
    # 'requests == 1.*',
]

DEV_REQUIREMENTS = [
    'black',
    'coveralls == 3.*',
    'flake8',
    'isort',
    'pytest == 6.*',
    'pytest-cov == 2.*',
]

setuptools.setup(
    name='roux',
    version='0.0.0',
    description='Your project description here',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/rraadd88/roux',
    author='USERNAME',
    license='MIT',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': DEV_REQUIREMENTS,
    },
    # entry_points={
    #     'console_scripts': [
    #         'PROJECT_NAME_URL=roux.my_module:main',
    #     ]
    # },
    python_requires='>=3.7, <4',
)
