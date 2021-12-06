from setuptools import setup, find_packages

setup(
    name='IrregConv',
    version='0.3',
    license='MIT',
    author="Bradford Gill",
    description='file: README.rst',
    author_email='bradfordgill@umass.edu',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='',
    keywords='IrregConv irregular convolution brain damage',
    install_requires=[
          'numpy',
      ],
)