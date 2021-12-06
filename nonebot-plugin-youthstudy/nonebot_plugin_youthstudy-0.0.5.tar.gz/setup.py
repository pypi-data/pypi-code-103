import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nonebot_plugin_youthstudy",                                     # 包的分发名称，使用字母、数字、_、-
    version="0.0.5",                                        # 版本号, 版本号规范：https://www.python.org/dev/peps/pep-0440/
    author="ayanamiblhx",                                       # 作者名字
    author_email="1196818079@qq.com",                      # 作者邮箱
    description="基于nonebot的青年大学习插件，用来获取最新一期的青年大学习答案",                            # 包的简介描述
    long_description=long_description,                      # 包的详细介绍(一般通过加载README.md)
    long_description_content_type="text/markdown",          # 和上条命令配合使用，声明加载的是markdown文件
    url="https://github.com/ayanamiblhx/nonebot_plugin_youthstudy",                              # 项目开源地址，我这里写的是同性交友官网，大家可以写自己真实的开源网址
    packages=['nonebot_plugin_youthstudy'],             
    package_data={'': ['*'],'nonebot_plugin_youthstudy': ['resource/bac/*','resource/font/*']},
    classifiers=[                                           # 关于包的其他元数据(metadata)
        "Programming Language :: Python :: 3",              # 该软件包仅与Python3兼容
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",           # 根据GPL许可证开源
        "Operating System :: OS Independent",               # 与操作系统无关
    ],
)
