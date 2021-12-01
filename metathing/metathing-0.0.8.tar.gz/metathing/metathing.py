#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from metathing.app import Service

class MetaThing():
    def __init__(self, config: object, srv_name: str):
        self.srv = Service(config, srv_name)

    def Bind(self, app:object):
        self.srv.Bind(app)

    def Run(self):
        self.srv.mqtt.connect()
        self.srv.http.Run()