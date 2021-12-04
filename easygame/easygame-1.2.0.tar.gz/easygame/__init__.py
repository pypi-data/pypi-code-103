"""
easygame

下载方式:
pip install easygame -i https://pypi.org/project

导入:
import easygame as eg

作者: stripe-python & Sunny
开源作品，已上传至pypi
"""

# easygame代码为中文注释

try:
    import os
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'true'
except os.error:
    pass

from easygame.colors import *
from easygame.screen import *
from easygame.widgets import *
from easygame.test import *
from easygame.errors import *

import sys
import pygame
version = sys.version_info
if version.major != 3:
    raise EasyGameError('please use python 3.6 or above')
if version.minor < 6:
    raise EasyGameError('please use python 3.6 or above')

version = pygame.version.vernum
if version < (2, 0, 1):
    raise EasyGameError('please use pygame 2.0.1 or above')

name = 'easygame'
