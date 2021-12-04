from setuptools import setup, find_packages
  
with open('requirements.txt') as f:
    requirements = f.readlines()
  
long_description = 'Trie for slingshot takehome.'

setup(
        name ='WordzFun',
        version ='1.1',
        author ='Sabad Modi',
        author_email ='sabadmodi@gmail.com',
        description ='Trie for slingshot takehome.',
        long_description = long_description,
        long_description_content_type ="text/markdown",
        license ='MIT',
        packages = find_packages(),
        entry_points ={
            'console_scripts': [
                'wordzfun = Trie.trie_cli:main'
            ]
        },
        classifiers =(
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ),
        keywords ='trie slingshot words dictionary wordzfun english',
        install_requires = requirements,
        zip_safe = False
)