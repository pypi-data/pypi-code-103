import setuptools

setuptools.setup(
    name="dta",
    version="1.0.1",
    author="Rukchad Wongprayoon",
    author_email="contact@biomooping.tk",
    description="dta Convert Dict To Attributes!",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dumb-stuff/dta",
    py_modules=["dta"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=2",
)