import setuptools

requirements = [
    'colorama'
]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="noob_utils",
    version="0.0.1",
    author="Leo Song",
    author_email="bjecdexlyb@gmail.com",
    description="Common Python Utils",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leordsong/noom_utils",
    project_urls={
        "Bug Tracker": "https://github.com/leordsong/noom_utils/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license='MIT',
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=requirements,
    python_requires=">=3.7",
)