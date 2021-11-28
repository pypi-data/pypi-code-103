import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="state_machine_py",
    version="1.0.0",
    author="muzudho",
    author_email="muzudho1@gmail.com",
    description="A state diagram machine package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/muzudho/state-machine-py",
    project_urls={
        "Bug Tracker": "https://github.com/muzudho/state-machine-py/issues",
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
