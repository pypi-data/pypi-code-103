from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'L2-boosting for high dimensional linear models'
LONG_DESCRIPTION = 'L2-boosting for high dimensional linear models'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="L2Boost", 
        version=VERSION,
        author="Bernhard Stankewitz",
        author_email="<stankebe@math.hu-berlin.de>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'first package'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)
