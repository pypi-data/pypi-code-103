from setuptools import setup, find_packages

setup(
    name             = 'pygifconvt_ka',
    version          = '1.0.5',
    description      = 'Test package for distribution',
    author           = 'ka',
    author_email     = 'a02a02a02@paran.com',
    url              = '',
    download_url     = '',
    install_requires = ['pillow'],
	include_package_data=True,
	packages=find_packages(),
    keywords         = ['GIFCONVERTER', 'gifconverter'],
    python_requires  = '',
    zip_safe=False,
    classifiers      = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
) 