from distutils.core import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')
setup(
  name = 'fz_word_finder',  
  packages = ['fz_word_finder'], 
  version = '0.0.1', 
  license='apache-2.0',
  description = "Fuzzy match word finder. Supports multiple simultaneous target strings and fuzzy match rules. (No regex or normalization)",
  author = 'Rairye', 
  url = 'https://github.com/Rairye/fz-word-finder',   
  download_url = 'https://github.com/Rairye/fz-word-finder/archive/refs/tags/v0.0.1.tar.gz',
  keywords = ['fuzzy', 'match', 'search'],
  long_description=long_description,
  long_description_content_type='text/markdown',

  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License', 
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.1',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)
