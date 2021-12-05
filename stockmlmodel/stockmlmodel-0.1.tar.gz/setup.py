from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='stockmlmodel',
  version='0.1',
  description='Stock Market Analysis',
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Vedant Jolly, Rishabh Jain, Sakshi Mahadik',
  author_email='vedantjolly2001@gmail.com,rishabhjainrj0110@gmail.com,sakshimahadik2511@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='stock market', 
  packages=find_packages(),
  install_requires=['sklearn','matplotlib','pandas','numpy'] 
)