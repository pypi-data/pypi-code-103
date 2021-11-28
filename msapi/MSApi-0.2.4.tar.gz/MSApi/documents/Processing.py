from typing import Optional
from datetime import datetime

from MSApi.ObjectMS import check_init
from MSApi.documents.DocumentMS import DocumentMS
from MSApi.MSLowApi import MSLowApi, error_handler, caching
from MSApi.State import State


class Processing(DocumentMS):

    @classmethod
    @caching
    def generate(cls, **kwargs):
        return MSLowApi.gen_objects('entity/processing', Processing, **kwargs)

    @classmethod
    def get_template_by_processing_order(cls, processing_order, **kwargs):
        json_data = {
            "processingOrder": {
                "meta": processing_order.get_meta().get_json()
            }
        }
        response = MSLowApi.auch_put(f'entity/processing/new', json=json_data, **kwargs)
        error_handler(response)
        return Processing(response.json())

    @classmethod
    def gen_states(cls):
        response = MSLowApi.auch_get(f"entity/processing/metadata")
        error_handler(response)
        for states_json in response.json()["states"]:
            yield State(states_json)

    def __init__(self, json):
        super().__init__(json)

    def create(self, **kwargs):
        response = MSLowApi.auch_post(f'entity/processing', json=self.get_json(), **kwargs)
        error_handler(response)
        self._json = response.json()

    @check_init
    def get_state(self) -> Optional[State]:
        return self._get_optional_object('state', State)
