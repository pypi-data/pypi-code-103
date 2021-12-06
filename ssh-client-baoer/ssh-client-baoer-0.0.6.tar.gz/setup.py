import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

install_requires = [
    "fabric==2.6.0",
]

setuptools.setup(
    name="ssh-client-baoer",
    version="0.0.6",
    author="baoer",
    author_email="821832333@qq.com",
    description="SSH Client.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=install_requires,
    url="https://gitee.com/haitaoboy/ssh-client",
    project_urls={
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
