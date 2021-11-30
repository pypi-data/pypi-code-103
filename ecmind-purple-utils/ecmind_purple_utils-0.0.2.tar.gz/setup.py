import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='ecmind_purple_utils',
    version='0.0.2',
    author='Ulrich Wohlfeil; Roland Koller',
    author_email='info@ecmind.ch',
    description='Helper for red and blue',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.ecmind.ch/open/ecmind_purple_utils',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    install_requires=[
    ],
    extras_require = { }
)