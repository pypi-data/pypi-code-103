from pytest_testrail_api_client.service import get_date_from_timestamp


class Case:
    def __init__(self, data: dict):
        if data is not None:
            self.id: int = data.get('id')
            self.title: str = data.get('title')
            self.section_id: int = data.get('section_id')
            self.template_id: int = data.get('template_id')
            self.type_id: int = data.get('type_id')
            self.priority_id: int = data.get('priority_id')
            self.milestone_id = data.get('milestone_id')
            self.refs: str = data.get('refs')
            self.created_by: int = data.get('created_by')
            self.created_on: int = get_date_from_timestamp(data.get('created_on'))
            self.updated_by: int = data.get('updated_by')
            self.updated_on: int = get_date_from_timestamp(data.get('updated_on'))
            self.estimate: str = data.get('estimate')
            self.estimate_forecast: str = data.get('estimate_forecast')
            self.suite_id: int = data.get('suite_id')
            self.display_order: int = data.get('display_order')
            self.is_deleted: int = data.get('is_deleted')
            self.custom_automation_type: int = data.get('custom_automation_type')
            self.custom_preconds = data.get('custom_preconds')
            self.custom_steps = data.get('custom_steps')
            self.custom_expected = data.get('custom_expected')
            self.custom_steps_separated: list = data.get('custom_steps_separated')
            self.custom_mission = data.get('custom_mission')
            self.custom_goals = data.get('custom_goals')
            self.custom_platform: list = data.get('custom_platform')
            self.custom_ui_type: list = data.get('custom_ui_type')

    def __str__(self):
        return self.title

    def is_equal(self, case):
        self_dict, case_dict = self.__dict__, case.__dict__
        if self.title == case.title:
            for attribute in ('section_id', 'type_id', 'estimate', 'milestone_id', 'priority_id', 'refs', 'suite_id',
                              'template_id'):
                if attribute in self_dict and attribute in case_dict:
                    if attribute == 'custom_steps_separated':
                        if not all((step['content'] == case.custom_steps_separated[index]['content'] for index, step in
                                    enumerate(self.custom_steps_separated))):
                            return False
                    elif str(self_dict[attribute]) != str(case_dict[attribute]):
                        return False
                else:
                    return False
            custom_attributes_self = {key: value for key, value in self_dict.items() if key.startswith('custom_')}
            custom_attributes_case = {key: value for key, value in case_dict.items() if key.startswith('custom_')}
            if custom_attributes_self != custom_attributes_case:
                return False
        return True


class CaseHistory:
    def __init__(self, data: dict):
        if data is not None:
            self.id: int = data.get('id')
            self.type_id: int = data.get('type_id')
            self.created_on: int = get_date_from_timestamp(data.get('created_on'))
            self.user_id: int = data.get('user_id')
            self.changes: list = data.get('changes')
