import setuptools

setuptools.setup(
    name="femopt",                     
    version="0.0.1",                        
    author="dewloosh",
    author_email = 'dewloosh@gmail.com',                    
    description="A package to optimize finite element models",
    packages=setuptools.find_packages(),   
    classifiers=[
        'Development Status :: 3 - Alpha',     
        'License :: OSI Approved :: MIT License',   
        'Programming Language :: Python :: 3',
		'Operating System :: OS Independent'
    ],                                      
    python_requires='>=3.6',                
    py_modules=["femopt"],             
    package_dir={'':'src'},     
    install_requires=[            
          'setuptools',
          'wheel',
      ],
)

