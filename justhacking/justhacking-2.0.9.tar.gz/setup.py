from setuptools import setup, find_packages
import os


VERSION = '2.0.9'
DESCRIPTION = 'Just Hacking is a Python CLI script that stimulates as you are hacking.'
LONG_DESCRIPTION = '''
```
░░█ █░█ █▀ ▀█▀   █░█ █░█ █▀▀ █▄▀ ▄█ █▄░█ █▀▀
█▄█ █▄█ ▄█ ░█░   █▀█ ▀▀█ █▄▄ █░█ ░█ █░▀█ █▄█
```

<a href=''><img src="https://img.shields.io/badge/justhacking-CLI Hacking Simulation-yellow.svg?logo=sharp"></a>
<a href=''><img src="https://img.shields.io/badge/Version-v2.0-orange.svg?logo=vectorworks"></a>
<a href='https://www.python.org/'><img src="https://img.shields.io/badge/Python-3-blue.svg?style=flat&logo=python"></a>
<a href='LICENSE'><img src="https://img.shields.io/badge/MIT-LICENCE-brightgreen.svg?logo=mitsubishi"></a>




<br>
<br>
<br>


# ▶️ __*pip*__ installation

IF you don't have '[pip](https://www.google.com/search?q=install+pip)' or '[python3](https://www.google.com/search?q=install+python+3)' installed - install them !

### Install *justinghacking* with simple command :
```
pip install justhacking
```
<br>

Command works for (& in) *Windows - Command Prompt | Linux & Mac OS - Terminal*


<br>
<br>


# ▶️ __*Git clone*__ installation

### Clone this *repository* with *git* :
```
git clone https://github.com/Divinemonk/justhacking/
```

### Then follow these commands 
```
cd justhacking
pip install -r requirements.py
python3 install setup.py
```


<br>
<br>
<br>


# 🪛 Usage

Open terminal or command line and type : `justhacking`

Done ! - Your fake hacking / hacking simulation setup is ready !!

'''


# Setting up
setup(
    name="justhacking",
    version=VERSION,
    author="Divinemonk",
    author_email="<v1b7rc8eb@relay.firefox.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url = 'https://github.com/Divinemonk/justhacking/',
    packages=['justhacking'],
    py_modules = ['jh_cmdcenter', 'jh_matrix','justhacking'],
    install_requires=['rich'],
    keywords=['python', 'justhacking', 'divinemonk', 'hacking stimulation', 'cli', 'python hacking', 'console'],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "justhacking=justhacking.__main__:starthack",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "License :: OSI Approved :: MIT License"
    ]
)