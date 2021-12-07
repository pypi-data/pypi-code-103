#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/8/30 11:10
# @Author  : oujianhua
# @mail  : ojhtyy@163.com
# @File    : env.py

import sys
import os
#设置工作路径为运行文件的所在路径
s_BaseDir=os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(s_BaseDir)
os.chdir(s_BaseDir)
