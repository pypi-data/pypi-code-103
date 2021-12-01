import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="liuxiankun-pytest-playwright1",
    version="0.0.3",  # 包版本
    author="liuxiankun",  # 作者
    author_email="939449414@qq.com",  # 作者邮箱
    description="A small example package",  # 工具包简单描述
    packages=setuptools.find_packages(),  # 不用动，会自动发现
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Framework :: Pytest",
    ],
    install_requires=[
        "playwright>=1.13",
        "pytest",
        "pytest-base-url",
        "python-slugify",
    ],
)