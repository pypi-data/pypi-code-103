#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/12/6 11:11
# @Author  : Adyan
# @File    : settings.py


from Utils import MongoPerson


class Settings:
    def __init__(self, host, port=None, db=None, table=None):
        if not port:
            port = 27017
        if not db:
            db = 'settings'
        if not table:
            table = 'config'
        config = MongoPerson(
            table, db,
            config={"host": host, "port": port}
        ).find_one()
        config.pop("_id")
        self.config = config
