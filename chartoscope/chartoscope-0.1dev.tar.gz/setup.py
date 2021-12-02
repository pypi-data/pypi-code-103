from distutils.core import setup

setup(
    name='chartoscope',
    version='0.1dev',
    packages=['chartoscope'],
    package_data={'chartoscope': ['lib/libchartoscope.so']},
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
)
