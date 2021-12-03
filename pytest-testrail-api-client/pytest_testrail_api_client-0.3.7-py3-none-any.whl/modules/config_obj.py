class Config:
    def __init__(self, data: dict):
        if data is not None:
            self.id: int = data.get('id')
            self.name: str = data.get('name')
            self.project_id: int = data.get('project_id')
            self.configs: list = [ConfigOfConfig(config) for config in data.get('configs')]

    def __str__(self):
        return self.name


class ConfigOfConfig:
    def __init__(self, data: dict):
        if data is not None:
            self.id: int = data.get('id')
            self.name: str = data.get('name')
            self.group_id: int = data.get('group_id')

    def __str__(self):
        return f'{self.name}, id = {self.id}'
