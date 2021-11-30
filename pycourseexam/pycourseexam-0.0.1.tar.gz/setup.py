from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 1 - Planning',
  'Intended Audience :: Education',
  'Operating System :: POSIX :: Linux',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='pycourseexam',
  version='0.0.1',
  description='Módulo para determinar alumnos que aprobaron el curso, dependiendo la secuencia de examenes (parcial, recuperatorio), la cantidad de examenes, y las notas para aprobarlos.',
  long_description_content_type="text/markdown",
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='@Mato',
  author_email='no@email.org',
  license='MIT', 
  classifiers=classifiers,
  keywords='student, course management, course, university', 
  packages=find_packages(),
  install_requires=[''] 
)
