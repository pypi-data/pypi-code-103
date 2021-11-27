import setuptools

setuptools.setup(
    author="MohammadReza Barghi",
    author_email="info@genesiscube.ir",
    name='autooptimizer',
    license="MIT",
    description='AutoOptimizer is a python package for optimize ML algorithms.',
    version='v0.1',
    long_description='README',
    url='https://github.com/mrb987/autooptimizer',
    packages=setuptools.find_packages(),
    python_requires=">=3",
    install_requires=['sklearn',
                      'numpy',
                      'matplotlib',
                      'mlxtend',],
    keyword=['python', 'machine learning', 'sklearn', 'data science'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',],
)
