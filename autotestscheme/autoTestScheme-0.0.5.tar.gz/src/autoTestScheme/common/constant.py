#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
__title__  = 
__Time__   = 2020/12/19 08:47
__Author__ = 熊润
"""
import os
import sys
import platform
import tempfile
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_FOLDER = tempfile.mkdtemp()

# 测试报告目录
REPORT_DIR = os.path.join(TMP_FOLDER, 'allure-results')
TMP_REPORT_DIR = os.path.join(TMP_FOLDER, 'allure-tmp-result')
TMP_REPORTS_DIR = os.path.join(TMP_FOLDER, 'allure-tmp-results')
if not os.path.exists(TMP_REPORTS_DIR):
    os.makedirs(TMP_REPORTS_DIR)
RUN_TMP_DIR = os.path.join(TMP_FOLDER, 'run_tmp')

PERFORMANCE_LOG_DIR = os.path.join(TMP_FOLDER, 'log')
ADDRESS_PATH = os.path.join(BASE_DIR, 'common', 'configure', 'address.json')

ALLURE_NAME = 'allure'
if platform.system() == 'Windows':
    ALLURE_NAME += ".bat"
ALLURE_PATH = os.path.join(BASE_DIR, 'allure', 'bin', ALLURE_NAME)
if platform.system() != 'Windows':
    subprocess.call("chmod 777 {}".format(ALLURE_PATH), shell=True)
