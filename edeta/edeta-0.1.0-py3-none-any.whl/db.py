#!/usr/bin/env python
# coding: utf-8

__all__ =['ProjectDB', 'BaseDB']

import os
from .abstract import AbstractDB


class ProjectDB(AbstractDB):
    def __init__(self, key=None):
        super().__init__(key=key or os.getenv('PROJECT_KEY'))
        

class BaseDB(AbstractDB):
    def __init__(self, key=None):
        super().__init__(key=key or os.getenv('BASE_KEY'))