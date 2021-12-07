from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

#'Operating System :: Microsoft :: Windows :: Windows 10',

setup(
    name='returnsPortfolio',
    version='0.0.1',
    description='Calculate portfolio returns',
    long_description='Using a time series of returns and a time series of weights for each asset, the function calculates the returns of a portfolio with the same periodicity of the returns data',
    url='',
    author='Shawn Jiang',
    author_email='shawnjiang619@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='return portfolio',
    packages=find_packages(),
    install_requires=['numpy',
                      'pandas',
                      'matplotlib',
                      'datetime',
                      'logging']
)

