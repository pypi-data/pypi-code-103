from setuptools import setup, find_packages

VERSION = '1.0.0-alpha.1'
DESCRIPTION = 'TextReader'
LONG_DESCRIPTION = 'TextReader'

# Setting up
setup(
        name="textreader", 
        version=VERSION,
        license='cc-by-sa-4.0',
        author="NA for now",
        author_email="<NA@gmail.com>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[],
        keywords=['python', 'text readability assessment'],
        classifiers=[
        'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        ],
)
