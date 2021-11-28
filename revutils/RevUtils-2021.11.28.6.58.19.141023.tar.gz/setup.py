# from distutils.core import setup
from setuptools import setup

setup(
    name='RevUtils',
    packages=['RevUtils'],
    version='2021.11.28.6.58.19.141023',
    license='MIT',
    description='Utils Created And Used By RevEngine3r',
    author='Saeed',
    author_email='RevEngine3r@Gmail.Com',
    url='https://github.com/RevEngine3r/RevUtilities',
    download_url='https://github.com/RevEngine3r/RevUtilities/archive/refs/heads/master.zip',
    keywords=['RAR', 'RevEngine3r', 'Persian', 'Tools'],
    install_requires=[
        'requests',
        'beautifulsoup4',
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    package_data={'RevUtils': ['*.exe']}
)
