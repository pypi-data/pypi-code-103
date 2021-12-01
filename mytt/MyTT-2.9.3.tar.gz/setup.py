#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: mpquant
# Mail: mpsoft163@163.com
# Created Time:  2018-4-16 19:17:34
#############################################

from setuptools import setup, find_packages            #这个包没有的可以pip一下

setup(
    name = "MyTT",      #这里是pip项目发布的名称
    version = "2.9.3",  #版本号，数值大的会优先被pip
    keywords = ("pip", "MyTT", "indicators"),
    description = "Mini Python library with most stock market indicators",
    long_description = "MyTT是您量化工具箱里的瑞士军刀，精炼而高效，它将通达信,同花顺,文华麦语言等指标公式indicators,最简移植到Python中,核心库单个文件，仅百行代码,实现和转换同花顺通达信所有常见指标MACD,RSI,BOLL,ATR,KDJ,CCI,PSY等,全部基于numpy和pandas的函数封装，简洁且高性能，能非常方便的应用在各自股票股市技术分析，股票自动程序化交易,数字货币BTC等量化等领域",
    license = "MIT Licence",

    url = "https://github.com/mpquant/MyTT",     #项目相关文件地址，一般是github
    author = "mpquant",
    author_email = "mpsoft163@163.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["numpy", "pandas", "requests"]          #这个项目需要的第三方库
)

