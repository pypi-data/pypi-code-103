from typing import List


class CaseField:
    def __init__(self, data: dict):
        if data is not None:
            self.id: int = data.get('id')
            self.is_active: bool = data.get('is_active')
            self.type_id: int = data.get('type_id')
            self.name: str = data.get('name')
            self.system_name: str = data.get('system_name')
            self.label: str = data.get('label')
            self.description: str = data.get('description')
            self.configs: List[CaseFieldConfig] = [CaseFieldConfig(config) for config in data.get('configs')]
            self.display_order: int = data.get('display_order')
            self.include_all: bool = data.get('include_all')
            self.template_ids: list = data.get('template_ids')

    def __str__(self):
        return self.label


class CaseFieldConfig:
    def __init__(self, data: dict):
        if data is not None:
            self.context: CaseFieldConfigContext = CaseFieldConfigContext(data.get('context'))
            self.options: CaseFieldConfigOptions = CaseFieldConfigOptions(data.get('options'))
            self.id: str = data.get('id')


class CaseFieldConfigContext:
    def __init__(self, data: dict):
        if data is not None:
            self.is_global: bool = data.get('is_global')
            self.project_ids = data.get('project_ids')


class CaseFieldConfigOptions:
    def __init__(self, data: dict):
        if data is not None:
            self.is_required: bool = data.get('is_required')
            self.default_value: str = data.get('default_value')
            self.format: str = data.get('format')
            self.rows: str = data.get('rows')
            items = data.get('items')
            if items is not None:
                self.items = {item.split(', ', maxsplit=1)[1]: item.split(', ', maxsplit=1)[0]
                              for item in items.split('\n')}
