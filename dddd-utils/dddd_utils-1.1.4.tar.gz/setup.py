import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

VERSION = "1.1.4"
setuptools.setup(
    name="dddd_utils",
    version=VERSION,
    author="MyYasuo666",
    author_email="author@example.com",
    description="带带弟弟小工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/duquan1995/dq-utils",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        'premailer>=3.1.0'
    ],
)
