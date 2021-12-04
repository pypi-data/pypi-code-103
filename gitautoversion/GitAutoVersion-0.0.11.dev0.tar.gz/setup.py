import setuptools

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="GitAutoVersion",
    version="0.0.11-dev",
    author="Sebastian GABRIEL",
    author_email="dev@3134.at",
    description="Get a descriptive version string in a git repository.",
    long_description = long_description,
    long_description_content_type="text/x-rst",
    url="https://gitlab.com/3134/GitAutoProject",
    project_urls={
        'Bug Tracker': "https://gitlab.com/3134/GitAutoProject/-/issues",
        'Source': 'https://gitlab.com/3134/GitAutoProject/',
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)