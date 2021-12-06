import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(name='codescan',
      version='0.2.0',
      description='Scans the code for security leaks',
      long_description=README,
      long_description_content_type="text/markdown",
      url='https://github.com/atparinas/codescan',
      author='Andy Parinas',
      author_email='andy.parinas@gmail.com',
      license='MIT',
      packages=['codescan'],
      install_requires=[
          'prettytable',
          'progress'
      ]
)