from setuptools import find_packages, setup
setup(
    name='pranky_shiprocket',
    packages=find_packages(include=['pranky_shiprocket']),
    version='0.1.1',
    description='Python Library for Shiprocket',
    author='Ankit Bhardwaj',
    license='MIT',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)