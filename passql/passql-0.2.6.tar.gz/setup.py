from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='passql',
      version='0.2.6',

      description='Super light ORM',
      long_description=long_description,
      long_description_content_type='text/markdown',

      author='Vladislav Mironov',
      author_email='hidden120@mail.ru',

      python_requires='>=3.6',
      classifiers=[
          'Programming Language :: Python :: 3.9',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
      ],

      packages=['passql'],
      zip_safe=False)
