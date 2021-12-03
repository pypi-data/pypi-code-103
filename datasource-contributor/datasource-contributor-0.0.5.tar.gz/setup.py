import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="datasource-contributor",
    version="0.0.5",
    author="Hale",
    author_email="hao.liang@tianrang-inc.com",
    description="A CUI tool that automatically crawls website data and contributes to http://www.citybrain.org",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://112.124.238.90/citybrain/tools/datasource-contributor.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'gitpython',
        'Scrapy'
    ],
    keywords='git tag datasource-contributor tagup tag-up version autotag auto-tag commit message',
    project_urls={
        'Homepage': 'http://112.124.238.90/citybrain/tools/datasource-contributor.git',
    },
    entry_points={
        'console_scripts': [
            'datasource-contributor=__main__:main',
        ],
    },
)
