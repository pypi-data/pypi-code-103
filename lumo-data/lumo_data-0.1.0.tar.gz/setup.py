from setuptools import setup, find_packages

"""
python3 setup.py sdist bdist_wheel; 
python3 setup.py sdist bdist_wheel; sudo pip install dist/$(python3 install.py);
python3 setup.py sdist bdist_wheel; pip install dist/$(python3 install.py) --user
python3 setup.py sdist bdist_wheel; pip install dist/$(python3 install.py) 
python3 setup.py sdist bdist_wheel; pip3 install dist/$(python3 install.py) 
sudo pip install dist/$(python3 install.py);
pip install dist/$(python3 install.py) --user
"""

setup(
    name='lumo_data',
    version='0.1.0',
    description='A bunch of optimzed data-related class for replacing the original pytorch DataLoader, Dataset, etc..',
    url='https://github.com/pytorch-lumo/lumo_data',
    author='sailist',
    author_email='sailist@outlook.com',
    license='Apache License 2.0',
    include_package_data=True,
    install_requires=[
        'loky'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='lumo loky multiprocess dataloader pytorch batch',
    packages=find_packages('.', exclude=('tests', 'example')),
    entry_points={
    },
)
