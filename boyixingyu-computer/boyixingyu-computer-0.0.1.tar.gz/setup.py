import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "boyixingyu-computer",
    version = "0.0.1",
    author = "boyixingyu",
    author_email = "boyixingyu@163.com",
    description = "计算加减乘除",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    include_package_data = True,
    packages = setuptools.find_packages(),
)