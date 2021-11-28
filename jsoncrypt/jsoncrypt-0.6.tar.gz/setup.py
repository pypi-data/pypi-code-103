from distutils.core import setup
setup(
  name = 'jsoncrypt',
  packages = ['jsoncrypt'],
  version = '0.6',
  license='MIT',
  description = 'Encryption and Decryption of JSON files and Dictionaries.',
  long_description = 'Encryption and Decryption of JSON files and Dictionaries.\nOption of adding a password and reading encrypted in memory.\nOption of saving dictionary encrypted or decrypted in a file as a json format.\nFor more information read file: README.md',
  long_description_content_type = 'text/markdown',
  author = 'Renne C. (GRC Algoritmos)',
  author_email = 'grc.algoritmos@gmail.com',
  url = 'https://github.com/grc-algoritmos/jsoncrypt',
  download_url = 'https://github.com/grc-algoritmos/jsoncrypt/archive/refs/tags/v_06.tar.gz',
  keywords = ['JSON', 'ENCRYPTION', 'DECRYPTION', 'ENCODE', 'OBFUSCATE'],
  install_requires=[],
  classifiers=[
    'Development Status :: 3 - Alpha', # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
