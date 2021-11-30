
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="polydata",                     
    version="0.0.1",                        
    author="dewloosh",
    author_email = 'dewloosh@gmail.com',
    url = 'https://github.com/dewloosh/polydata',   
    download_url = 'https://github.com/dewloosh/polydata/archive/refs/tags/0_0_1.zip',                     
    description="A package to build and manage polygonal data",
    long_description=long_description,   
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),   
    classifiers=[
        'Development Status :: 3 - Alpha',     
        'License :: OSI Approved :: MIT License',   
        'Programming Language :: Python :: 3',
		'Operating System :: OS Independent'
    ],                                      
    python_requires='>=3.6',                
    py_modules=["polydata"],             
    package_dir={'':'src'},     
    install_requires=[            
          'setuptools',
          'wheel',
          'comtypes',
          'pywin32'
      ],
)

