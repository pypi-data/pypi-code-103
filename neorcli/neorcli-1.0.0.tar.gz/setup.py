from setuptools import setup, find_packages
  
with open('requirements.txt') as f:
    requirements = f.readlines()
  
long_description = 'NeorCloud CLI tool to manage your services from cli.'
  
setup(
        name ='neorcli',
        version ='1.0.0',
        author ='Ali Ghotbizadeh',
        author_email ='ali.ghotbizadeh@gmail.com',
        url ='https://github.com/NeorCloud/neor-cli',
        description ='NeorCli tool',
        long_description = long_description,
        long_description_content_type ="text/markdown",
        license ='MIT',
        packages = find_packages(),
        entry_points ={
            'console_scripts': [
                'neorcli = src.cli:main'
            ]
        },
        classifiers =(
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ),
        keywords ='NeorCloud NeorCli',
        install_requires = requirements,
        zip_safe = False
)