import setuptools

setuptools.setup(
    name='aas-r',
    version='0.0.1',
    author='Xeouz',
    description='Faster Get Requests with AIOHTTP',
    long_description=open('README.md','r').read(),
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"],
    zip_safe=True,
    python_requires='>=3.6',
)