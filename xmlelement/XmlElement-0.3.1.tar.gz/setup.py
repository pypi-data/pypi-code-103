import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='XmlElement',
    version='0.3.1',
    author='Roland Koller',
    author_email='info@ecmind.ch',
    description='A simpler XML writer and xml-to-dict converter',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.ecmind.ch/open/xmlelement',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)