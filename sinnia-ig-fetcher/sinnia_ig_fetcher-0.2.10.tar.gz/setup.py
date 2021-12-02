from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(name='sinnia_ig_fetcher',
      version='0.2.10',
      description='Sinnia IG Fetching Tools',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/sinnia/scripts/tree/develop/instagram',
      author='Sinnia',
      author_email='sonia.segura@sinnia.com',
      packages=find_packages(),
      include_package_data=True,
      package_dir={'sinnia_ig_fetcher': 'sinnia_ig_fetcher'},
      package_data={'sinnia_ig_fetcher': ['conf/*.yaml']},
      install_requires=[
        'python-instagram',
        'instagram',
        'pymysql',
        'pyyaml',
        'requests',
        'sinnia_shared'
      ],
      zip_safe=False)


