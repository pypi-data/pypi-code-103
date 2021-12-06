from distutils.core import setup
setup(
  name = 'AGONS',         
  packages = ['AGONS'],   
  version = '1.0.9',    
  license='MIT',       
  description = 'Package to use Yigit Lab Developed AGONS Algorithm for nanoparticle based sensor arrays',   
  author = 'Christopher Smith',                   
  author_email = 'c.w.smith022@gmail.com',      
  url = 'https://github.com/CWSmith022/yigit-lab',   
  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    
  keywords = ['nanosensors', 'fluorescence', 'automation', 'feature selection'],   
  install_requires=[            
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
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9'
  ],
)