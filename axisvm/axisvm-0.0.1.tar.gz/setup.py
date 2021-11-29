from distutils.core import setup

setup(
  name = 'axisvm',         
  packages = ['src.axisvm'],   
  version = '0.0.1',      
  license='MIT',        
  description = 'A python package for AxisVM',   
  author = 'Inter-CAD Ltd',                  
  author_email = 'bbalogh@axisvm.eu',     
  url = 'https://github.com/AxisVM/pyaxisvm',   
  download_url = 'https://github.com/AxisVM/pyaxisvm/archive/refs/tags/v_0_0_1.tar.gz',   
  keywords = ['AxisVM', 'Axis', 'Civil Engineering'],   
  install_requires=[            
          'setuptools',
          'wheel',
          'comtypes',
          'pywin32'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',     
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
  ],
)