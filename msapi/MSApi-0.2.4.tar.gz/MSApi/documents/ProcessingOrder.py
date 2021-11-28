from typing import Optional
from datetime import datetime

from MSApi.ObjectMS import ObjectMS, check_init
from MSApi.MSLowApi import MSLowApi, error_handler, string_to_datetime, caching
from MSApi.State import State
from MSApi.Organization import Account
from MSApi.Project import Project
from MSApi.Attribute import Attribute
from MSApi.documents.Processing import Processing
from MSApi.documents.ProcessingPlan import ProcessingPlan


class ProcessingOrder(ObjectMS):

    _type_name = 'processingorder'

    @classmethod
    @caching
    def generate(cls, **kwargs):
        return MSLowApi.gen_objects('entity/processingorder', ProcessingOrder, **kwargs)

    @classmethod
    def gen_states(cls):
        response = MSLowApi.auch_get(f"entity/processingorder/metadata")
        error_handler(response)
        for states_json in response.json()["states"]:
            yield State(states_json)

    def __init__(self, json):
        super().__init__(json)

    @check_init
    def get_id(self) -> str:
        return self._json.get('id')

    @check_init
    def get_account_id(self) -> str:
        return self._json.get('accountId')

    @check_init
    def get_sync_id(self) -> Optional[str]:
        return self._json.get('syncId')

    @check_init
    def get_updated_time(self) -> datetime:
        return string_to_datetime(self._json.get('updated'))

    @check_init
    def get_deleted_time(self) -> Optional[datetime]:
        return self._get_optional_object('deleted', string_to_datetime)

    @check_init
    def get_name(self) -> str:
        return self._json.get('name')

    @check_init
    def get_description(self) -> Optional[str]:
        return self._json.get('description')

    @check_init
    def get_code(self) -> Optional[str]:
        return self._json.get('code')

    @check_init
    def get_external_code(self) -> Optional[str]:
        return self._json.get('externalCode')

    @check_init
    def get_moment_time(self) -> datetime:
        return string_to_datetime(self._json.get('moment'))

    @check_init
    def is_applicable(self) -> bool:
        return bool(self._json.get('applicable'))

    @check_init
    def get_project(self) -> Optional[Project]:
        return self._get_optional_object('project', Project)

    @check_init
    def get_state(self) -> Optional[State]:
        return self._get_optional_object('state', State)

    @check_init
    def gen_attributes(self):
        for attr in self._json.get('attributes', []):
            yield Attribute(attr)

    def get_attribute_by_name(self, name: str) -> Optional[Attribute]:
        for attr in self.gen_attributes():
            if attr.get_name() == name:
                return attr
        return None

    @check_init
    def get_organization_account(self) -> Optional[Account]:
        result = self._json.get('organizationAccount')
        if result is not None:
            return Account(result)
        return None

    @check_init
    def get_processing_plan(self) -> ProcessingPlan:
        return ProcessingPlan(self._json.get('processingPlan'))

    @check_init
    def get_quantity(self) -> int:
        return int(self._json.get('quantity'))

    @check_init
    def gen_processings(self):
        for attr in self._json.get('processings', []):
            yield Processing(attr)
