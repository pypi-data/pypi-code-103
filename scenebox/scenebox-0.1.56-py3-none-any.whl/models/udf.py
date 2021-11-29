#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#

class UDFError(Exception):
    pass


class Enricher(object):
    version = "0.0.1"

    def __init__(self,
                 scene_engine_client):

        self.scene_engine_client = scene_engine_client

    def enrich(self, metadata: dict) -> dict:
        pass


class Script(object):
    version = "0.0.1"

    def __init__(self,
                 scene_engine_client,
                 job_manager_client,
                 es_client,
                 logger,
                 ):

        self.scene_engine_client = scene_engine_client
        self.job_manager_client = job_manager_client
        self.es_client = es_client
        self.logger = logger

    def execute(self, **kwargs):
        pass