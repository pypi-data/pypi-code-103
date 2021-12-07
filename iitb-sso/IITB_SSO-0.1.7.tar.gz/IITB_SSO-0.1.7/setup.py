from setuptools import setup
# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "Readme.md").read_text()
setup(
    name='IITB_SSO',
    version='0.1.7', 
    long_description=long_description,
    long_description_content_type='text/markdown' , 
    description='Python package to integrate IIT Bomaby SSO login to your project',
    url='https://github.com/NihalSargaiya9/IITB-SSO',
    author='Nihal Sargaiya',
    author_email='nihalsargaiya4@gmail.com',
    license='MIT',
    packages=[],
    install_requires=["Flask>=2.0.2",
"python-dotenv>=0.19.2",
"requests>=2.26.0",
"setuptools>=59.0.1",
"Werkzeug==2.0.2" ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)