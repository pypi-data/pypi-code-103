from setuptools import setup

# https://betterscientificsoftware.github.io/python-for-hpc/tutorials/python-pypi-packaging/
# 1. Change version in this file and init
# 2. Run-> python setup.py sdist
# 3. Run-> python setup.py bdist_wheel --universal
# 4. Upload test-> twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# 5. Upload-> twine upload dist/*

setup(
    name='ootkintercanvas',
    version='0.3.0',
    description='An Object Oriented Extention for tkinter Canvas',
    url='https://gitlab.com/esrari/ootkintercanvas',
    author='Alireza Esrari',
    author_email='alireza.esrari@gmail.com',
    license='BSD 2-clause',
    packages=['ootkintercanvas'],
    install_requires=['tk',
                      'cv2',
                      'PIL'],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Topic :: Multimedia :: Graphics :: Editors :: Vector-Based',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Version Control :: Git',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.8',
    ],
)
