from setuptools import setup, find_packages

setup(
    name             = 'pygifconvert_test_din',
    version          = '1.0.0',
    description      = 'Test package for distribution',
    author           = 'heyazoo1007',
    author_email     = 'heyazoo1007@gmail.com',
    url              = '',
    download_url     = '',
    install_requires = ['pillow'],#실행하려면 다운받아야하는 패키지
	include_package_data=True, #required
	packages=find_packages(),
    keywords         = ['GIFCONVERTER', 'gifconverter'],
    python_requires  = '>=3',
    zip_safe=False,
    classifiers      = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
) 