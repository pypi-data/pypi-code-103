import pathlib
from setuptools import find_packages, setup

Here = pathlib.Path(__file__).parent

README = (Here / "README.md").read_text()

setup(
    name='imageSizeReducer',
    packages=find_packages(include=['imageSizeReducer']),
    version='0.2.0',
    description='Reduce image size',
    long_description=README,
    long_description_content_type="text/markdown",
    author='Bramhesh Kumar Srivastava',
    author_email='brahmesh1996@gmail.com',
    license='MIT',
    install_requires=['pillow', 'python-math'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
    classifiers = [
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ]
)