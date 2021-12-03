import setuptools
from pathlib import Path  # 这个是为了long_discription的
setuptools.setup(
    name="hongpdf",  # 名字尽量不要重复
    version=1.0,
    long_discription=Path("README.md").read_text(),  # 这样就连接过去了
    packages=setuptools.find_packages(exclude=["tests", "data"])
    # 跟他们说具体是哪一个packages是用来distribute的,后面括号[]的部分使用来排除的
)
