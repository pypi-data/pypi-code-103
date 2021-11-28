from setuptools import setup, Extension



with open("Readme.md", 'r') as f:
    long_description = f.read()

setup(name='kage-genotyper',
      version='0.0.2',
      description='KAGE',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/ivargr/kage',
      author='Ivar Grytten',
      author_email='',
      license='MIT',
      packages=["kage"],
      zip_safe=False,
      install_requires=['numpy', 'tqdm', 'pyfaidx', 'pathos', 'cython', 'scipy',
                        'obgraph',
                        'graph_kmer_index',
                        'kmer_mapper'
                        ],
      include_dirs=["."],
      classifiers=[
            'Programming Language :: Python :: 3'
      ],
      entry_points={
            'console_scripts': ['kage=kage.command_line_interface:main']
      }

)

""""
rm -rf dist
python3 setup.py sdist
twine upload --skip-existing dist/*
"""