from setuptools import setup, find_packages


setup(
    name='IrregConv',
    version='0.1',
    license='MIT',
    author="Bradford Gill",
    author_email='bradfordgill@umass.edu',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='',
    keywords='IrregConv irregular convolution brain damage',
    install_requires=[
          'numpy',
      ],

)