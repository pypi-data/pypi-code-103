import setuptools
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "Readme.md").read_text()

setuptools.setup(
    name='IITB_SSO',                 # This is the name of the package
    version="1.0.0",                        # The initial release version
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=["IITB_SSO"],             # Name of the python package
    package_dir={'':'IITB_SSO/src'},     # Directory of the source code of the package
     long_description=long_description,
    long_description_content_type='text/markdown' , 
    description='Python package to integrate IIT Bomaby SSO login to your project',
    url='https://github.com/NihalSargaiya9/IITB-SSO',
    author='Nihal Sargaiya',
    author_email='nihalsargaiya4@gmail.com',
    license='MIT',
    install_requires=["Flask>=2.0.2",
                "python-dotenv>=0.19.2",
                "requests>=2.26.0",
                "setuptools>=59.0.1",
                "Werkzeug==2.0.2" ],

    
)