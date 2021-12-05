import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="smModule",
    version="9.0.0",
    author="Pascal Vallaster",
    description="Fixed bugs, spelling and completed README",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(where="sm/src"),
    install_reqires=["_sqlite3", "platform", "smtplib", "fractions", "colorama", "xml"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=["sm"],
    package_dir={'': 'sm/src'},
)
