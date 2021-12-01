import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="liuxiankun-pytest-playwright1",
    version="0.0.1",  # 包版本
    author="liuxiankun",  # 作者
    author_email="939449414@qq.com",  # 作者邮箱
    description="A small example package",  # 工具包简单描述
    packages=setuptools.find_packages(),  # 不用动，会自动发现
    classifiers=[  # 给出了指数和点子你的包一些额外的元数据
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)