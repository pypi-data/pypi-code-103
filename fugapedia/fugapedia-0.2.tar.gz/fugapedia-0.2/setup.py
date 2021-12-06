from setuptools import setup, find_packages

setup(name='fugapedia',
      version='0.2',
      url='https://fugapedia.xyz/api.php',
      license='MIT',
      author='Karonus',
      author_email='0karonus0@gmail.com',
      description='Fugapedia API library for fugapedia.xyz',
      packages=find_packages(exclude=['fugapedia']),
      long_description_content_type="text/markdown",
      long_description=open('README.md').read(),
      zip_safe=False
      )
