from kntgen.str_helpers import *


@auto_str
class ProjectInfo:
    def __init__(self, project, developer, company, project_id):
        self.project = project
        self.developer = developer
        self.company = company
        self.project_id = project_id
