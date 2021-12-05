# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['preprocess', 'filetypeDetector', 'imageConverter', 'PIL2CV']
install_requires = \
['autocorrect>=2.6.0,<3.0.0',
 'fire>=0.4.0,<0.5.0',
 'opencv-python>=4.5.4.60,<5.0.0.0',
 'pdf2image>=1.16.0,<2.0.0',
 'pytesseract>=0.3.8,<0.4.0']

entry_points = \
{'console_scripts': ['OCR = main:text_detect']}

setup_kwargs = {
    'name': 'ocr-pdf-jpg-png',
    'version': '0.9.0',
    'description': 'Tesseract OCR with OpenCV preprocessing and auto-correct.',
    'long_description': None,
    'author': 'Vsevolod Mineev',
    'author_email': 'vsevolod.mineev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
