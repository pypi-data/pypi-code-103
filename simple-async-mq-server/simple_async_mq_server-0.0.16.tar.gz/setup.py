# from distutils.core import setup
from setuptools import setup, find_packages
setup(
  name = 'simple_async_mq_server',         # How you named your package folder (MyLib)
  #packages = ['simple_async_mq_server/'],
  packages = find_packages(where='simple_async_mq_server.*'),
  version = '0.0.16',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'A simple async message queue server - socket-io wrapper',   # Give a short description about your library
  author = 'Oliver Kramer',                   # Type in your name
  author_email = '3520.kramer@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/3520kramer/simple-async-mq-server',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/3520kramer/simple-async-mq-server/archive/v_0016.tar.gz',    # I explain this later on
  keywords = ['mq', 'async', 'server'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'asyncio',
          'python-socketio',
          'aiohttp',
          'aiohttp_cors',
          'dict2xml',
          'xmltodict',
          'mysql-connector-python'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.9',      #Specify which pyhton versions that you want to support
  ],
)