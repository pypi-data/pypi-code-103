import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="triton_bert",
    version="0.0.1",
    author="Yongwen Yan",
    author_email="yyw794@126.com",
    description="easy to use bert with nvidia triton server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://codechina.csdn.net/yyw794/triton_bert",
    packages=setuptools.find_packages(),
    install_requires=['tritonclient', 'transformers', 'more-itertools'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)