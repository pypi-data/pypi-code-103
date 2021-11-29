from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='lambdata-nicpapenburg',
  version='0.0.1',
  description='Learning to upload a package',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Nicholas Papenburg',
  author_email='nicpapenburg@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords=['lambda', 'bloomtech'], 
  packages=find_packages(),
  install_requires=['pandas', 'numpy'] 
)