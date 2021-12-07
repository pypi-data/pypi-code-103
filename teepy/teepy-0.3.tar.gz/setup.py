from distutils.core import setup
setup(
  name = 'teepy',
  packages = ['teepy'],
  version = '0.3',
  license = 'MIT',
  description = 'Tech Engineering Exam in Python',
  author = 'William Long',
  author_email = 'admin@longapalooza.com',
  url = 'https://github.com/longapalooza/teepy',
  download_url = 'https://github.com/longapalooza/teepy/archive/refs/tags/v0.3-beta.tar.gz',
  keywords = ['Tech', 'Exam', 'Engineering'],
  install_requires = [
          'beautifulsoup4',
          'cefpython3',
          'pint',
          'pyppeteer',
          'xlsxwriter',
      ],
  classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
  ],
  package_data = {
    "": ['teepy.html', 'teepy.css'],    
  },
)