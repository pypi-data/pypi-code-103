import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="engo-data-cli",
    version="0.0.5",
    author="caryyu",
    author_email="caryy.tg@gmail.com",
    description="A handy tool to import data onto cloud databases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/soft-union/engo-data-cli",
    project_urls={
        "Bug Tracker": "https://github.com/soft-union/engo-data-cli/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.24.0",
        "click>=7.1.2",
        "beautifulsoup4>=4.9.3"
    ],
    entry_points ={
        'console_scripts': [
            'engo-data-cli = cli.main:startbucks'
        ]
    },
)
