import sys
from setuptools import setup

import src as si

setup(
    version = si.__version__,
    license = si.__license__,
    author = si.__author__,
    url = si.__url__,
    download_url = 'https://pypi.org/project/sphindexer/',
    project_urls = {
        'Code': 'https://github.com/KaKkouo/sphindexer',
        'Issue tracker': 'https://github.com/KaKkouo/sphindexer/issues',
    }
)
