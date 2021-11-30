#!/usr/bin/env python
# coding: utf-8

__all__ =['ProjectDB', 'BaseDB']

import os
from starlette.config import Config
from edeta.abstract import AbstractDB

workdir = os.getcwd()
envfile = os.path.join(workdir, '.env')
env = Config(env_file=envfile)


class ProjectDB(AbstractDB):
    def __init__(self, key=None):
        super().__init__(key=key or env.get('PROJECT_KEY'))
        

class BaseDB(AbstractDB):
    def __init__(self, key=None):
        super().__init__(key=key or env.get('BASE_KEY'))
        
        