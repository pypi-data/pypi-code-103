from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='fireboard_cloud_api_client',
    version='0.0.1',
    url='https://github.com/gordlea/python_fireboard_cloud_api_client',
        project_urls={
        "Bug Tracker": "https://github.com/gordlea/python_fireboard_cloud_api_client/issues",
    },
    description='A rest api client for your fireboard thermometer',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='gordlea',
    author_email='jgordonlea@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        "Topic :: Home Automation"
    ],
    keywords='Fireboard cloud api async',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        "aiohttp>=3.8.0"
    ],
    python_requires=">=3.4",
)
