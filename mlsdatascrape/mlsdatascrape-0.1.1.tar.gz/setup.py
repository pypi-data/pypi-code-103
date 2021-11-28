from distutils.core import setup
setup(
  name='mlsdatascrape',
  packages=['mlsdatascrape'],
  version='0.1.1',
  license='MIT',
  description='Package for scraping Fbref.com for MLS data',
  author='Douglas Mellon',
  author_email='dm@dougmellon.com',
  url='https://dougmellon.com',
  download_url='https://github.com/dougmellon/mlsdatascrape/archive/refs/tags/0.1.1.tar.gz',
  keywords=['MLS', 'Socer', 'Scraping'],
  install_requires=[
          'BeautifulSoup4',
          'requests',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)