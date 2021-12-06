from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='csv2cleartable',
  version='0.0.1',
  description='Convert into csv into a readable table ',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='bharathraj',
  author_email='x20225024@student.ncirl.ie',
  license='MIT', 
  classifiers=classifiers,
  keywords='csv2table', 
  packages=find_packages(),
  install_requires=['os','StringIO','sys'] 
)
