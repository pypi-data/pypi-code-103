import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3.8'
]
 
setup(
  name='bianary_decision_parameter',
  version='0.2',
  description='bianary_classification',
  long_description=README,
  long_description_content_type="text/markdown",
  author='MAINAK RAY',
  author_email='mainakr748@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='decision', 
  packages=['bianary_decision_parameter'],
  install_requires=['sklearn','pandas','numpy'] 
  )
