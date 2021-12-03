# -*- coding:utf-8 -*-
from ..libs.fastapi import FastAPI


class ZApi(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
