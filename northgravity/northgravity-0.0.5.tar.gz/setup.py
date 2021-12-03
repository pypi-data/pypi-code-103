import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="northgravity",
    version="0.0.5",
    author="NorthGravity",
    author_email="info@northgravity.com",
    description="Python SDK for NorthGravity platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.northgravity.com/",
    packages=setuptools.find_packages(),
    classifiers=["Programming Language :: Python :: 3",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent"
                 ],
    python_requires='>=3.6',
)
