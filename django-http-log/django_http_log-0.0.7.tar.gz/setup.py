#!/user/bin/env python3
# -*- coding: utf-8 -*-
"""
--------------------------------------
    Author:     JiChao_Song
    Date  :     2021/11/21 下午8:00
    Desc  :
--------------------------------------
"""
import os

import setuptools

CUR_DIR = os.path.abspath(os.path.dirname(__file__))
README = os.path.join(CUR_DIR, "README.md")
with open("README.md", "r") as fd:
    long_description = fd.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.
setuptools.setup(
    name = 'django_http_log',

    version = '0.0.7',

    description = '记录django, http请求日志，并存到mongodb中',

    long_description = long_description,

    long_description_content_type = "text/markdown",

    url = "https://gitee.com/zhsjch/django_http_log.git",

    author = "JiChaoSong",

    author_email = "jichaosong@outlook.com",

    packages = ["django_http_log"],

    install_requires = [
        "django>=3.2.5",
        "mongoengine>=0.23.1",
        "django-rest-framework-mongoengine>=3.4.1",
        "djangorestframework>=3.12.4"
    ],

    include_package_data = True,

)
