from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dxp",
    version="0.1.1",
    license='MIT',
    author="Joseph Diza",
    author_email="josephm.diza@gmail.com",
    description="Library for analyzing CSV data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jmdaemon/dxp",
    project_urls={ "Bug Tracker": "https://github.com/jmdaemon/dxp/issues", },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires=">=3.6",
    py_modules=['dxp.util', 'dxp.lab'],
    install_requires=['argparse',],
    scripts=['scripts/dplt', 'scripts/tpose'],
    entry_points={
        'console_scripts': [
            'dxp = dxp.cli:main',
        ],
    },
    test_suite='tests',
)
