from setuptools import setup, find_packages

setup(
    name="test-pypi-package-1",
    version="0.6",
    license="MIT",
    author="Orvin Demsh",
    author_email="orvindemsy@gmail.com",
    package=find_packages("src"),
    package_dir={'':'src'},
    url='https://github.com/orvindemsy/test-pypi-package-1',
    keywords='example project',
    install_requires=[
        'scikit-learn',
    ],
)