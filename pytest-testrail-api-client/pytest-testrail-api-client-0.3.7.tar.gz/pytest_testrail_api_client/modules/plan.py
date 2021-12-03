from itertools import chain
from typing import List

import pytest_testrail_api_client.service as service


class Run:
    def __init__(self, data: dict):
        if data is not None:
            self.id: int = data.get('id')
            self.suite_id: int = data.get('suite_id')
            self.name: str = data.get('name')
            self.description = data.get('description')
            self.milestone_id = data.get('milestone_id')
            self.assignedto_id = data.get('assignedto_id')
            self.include_all: bool = data.get('include_all')
            self.is_completed: bool = data.get('is_completed')
            self.completed_on = service.get_date_from_timestamp(data.get('completed_on'))
            self.passed_count: int = data.get('passed_count')
            self.blocked_count: int = data.get('blocked_count')
            self.untested_count: int = data.get('untested_count')
            self.retest_count: int = data.get('retest_count')
            self.failed_count: int = data.get('failed_count')
            self.custom_status1_count: int = data.get('custom_status1_count')
            self.custom_status2_count: int = data.get('custom_status2_count')
            self.custom_status3_count: int = data.get('custom_status3_count')
            self.custom_status4_count: int = data.get('custom_status4_count')
            self.custom_status5_count: int = data.get('custom_status5_count')
            self.custom_status6_count: int = data.get('custom_status6_count')
            self.custom_status7_count: int = data.get('custom_status7_count')
            self.project_id: int = data.get('project_id')
            self.plan_id: int = data.get('plan_id')
            self.entry_index: int = data.get('entry_index')
            self.entry_id: str = data.get('entry_id')
            self.config: str = data.get('config')
            self.config_ids: list = data.get('config_ids')
            self.created_on = service.get_date_from_timestamp(data.get('created_on'))
            self.refs: str = data.get('refs')
            self.created_by: int = data.get('created_by')
            self.url: str = data.get('url')

    def __str__(self):
        return self.config if self.config is not None else self.name


class Entries:
    def __init__(self, data: dict):
        if data is not None:
            self.id: str = data.get('id')
            self.suite_id: int = data.get('suite_id')
            self.name: str = data.get('name')
            self.refs: str = data.get('refs')
            self.description = data.get('description')
            self.include_all: bool = data.get('include_all')
            self.runs: List[Run] = [Run(run) for run in data.get('runs')]

    def __str__(self):
        return self.name


class Plan:
    def __init__(self, data: dict):
        if data is not None:
            self.id: int = data.get('id')
            self.name: str = data.get('name')
            self.description: str = data.get('description')
            self.milestone_id = data.get('milestone_id')
            self.assignedto_id = data.get('assignedto_id')
            self.is_completed: bool = data.get('is_completed')
            self.completed_on = service.get_date_from_timestamp(data.get('completed_on'))
            self.passed_count: int = data.get('passed_count')
            self.blocked_count: int = data.get('blocked_count')
            self.untested_count: int = data.get('untested_count')
            self.retest_count: int = data.get('retest_count')
            self.failed_count: int = data.get('failed_count')
            self.custom_status1_count: int = data.get('custom_status1_count')
            self.custom_status2_count: int = data.get('custom_status2_count')
            self.custom_status3_count: int = data.get('custom_status3_count')
            self.custom_status4_count: int = data.get('custom_status4_count')
            self.custom_status5_count: int = data.get('custom_status5_count')
            self.custom_status6_count: int = data.get('custom_status6_count')
            self.custom_status7_count: int = data.get('custom_status7_count')
            self.project_id: int = data.get('project_id')
            self.created_on: int = service.get_date_from_timestamp(data.get('created_on'))
            self.created_by: int = data.get('created_by')
            self.url: str = data.get('url')
            if data.get('entries') is not None:
                self.entries: List[Entries] = [Entries(entrie) for entrie in data.get('entries')]

    def __str__(self):
        return self.name

    def get_run_from_entry_name_and_config(self, name: str, config: str) -> Run:
        entries = tuple(entry.runs for entry in self.entries if entry.name.lower() == name.lower())
        if len(entries) > 0:
            result = [run for run in tuple(chain.from_iterable(entries)) if run.config.lower() == config.lower()]
            return result[0] if len(result) > 0 else None
