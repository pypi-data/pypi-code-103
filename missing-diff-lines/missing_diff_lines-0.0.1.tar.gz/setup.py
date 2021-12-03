import pathlib
from setuptools import setup, find_packages
from distutils.core import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name='missing_diff_lines',
    url='https://github.com/tom-010/missing_diff_lines',
    version='0.0.1',
    author='Thomas Deniffel',
    author_email='tdeniffel@gmail.com',
    packages=['missing_diff_lines'], # find_packages(),
    license='Apache2',
    install_requires=[
        'coverage'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    description='Creates a set of all lines that have no test coverage in the current git diff',
    long_description=README,
    long_description_content_type="text/markdown",
    python_requires='>=3',
    include_package_data=True,
    entry_points={
    }
)