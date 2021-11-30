import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="rfsdk",
    version="0.4.1",
    author="loufu",
    author_email="loufu.2004@163.com",
    description="No description.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
	include_package_data=True,
    install_requires=[
        'protobuf'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows :: Windows 7",
    ],
)