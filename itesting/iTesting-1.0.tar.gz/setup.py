# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='iTesting',
    version='1.0',
    description='拉勾教育专栏<测试开发入门与实战>示例，仅为演示如何上传PyPI使用。',
    long_description='''此代码仓库为本人拉勾教育专栏<测试开发入门与实战>的配套练习仓库.\n
    更多关于自动化测试框架的内容，请关注我的公众号iTesting.\n
    另:\n
    对自主开发自动化测试框架感兴趣的同学，可购买我的新书<从0到1搭建自动化测试框架：原理、实现与工程实践>.\n
    对JavaScript及前端自动化测试感兴趣的同学，可购买我的另一本书<前端自动化测试框架 -- Cypress从入门到精通>.\n
                                                                      ---Kevin Cai（2021.12）\n
    ''',
    author='kevin.cai',
    author_email='testertalk@outlook.com',
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'pytest',
        'pyyaml'
    ],
    packages=find_packages(),
    license='MIT',
    url='https://www.helloqa.com',
    entry_points={
        'console_scripts': [
            'iTesting = iTesting.main:main'
        ]
    }
)
