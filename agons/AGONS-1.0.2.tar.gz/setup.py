from distutils.core import setup
setup(
  name = 'AGONS',         # How you named your package folder (MyLib)
  packages = ['AGONS'],   # Chose the same as "name"
  version = '1.0.2',    
  license='MIT',       
  description = 'Package to use Yigit Lab Developed AGONS Algorithm for nanoparticle based sensor arrays',   # Give a short description about your library
  author = 'Christopher Smith',                   # Type in your name
  author_email = 'c.w.smith022@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/CWSmith022/yigit-lab',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['nanosensors', 'fluorescence', 'automation', 'feature selection'],   
  install_requires=[            # I get to this in a second
          'IPython',
          'matplotlib',
          'ipympl',
          'seaborn',
          'sklearn',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',  
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9'
  ],
)