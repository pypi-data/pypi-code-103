""" This module implement tasks functionality  """
from superwise.controller.base import BaseController


class TaskController(BaseController):
    """Class TaskController - responsible for task functionality"""

    def __init__(self, client, sw):
        """
        Constructor of TaskController class
        """
        super().__init__(client, sw)
        self.path = "admin/v1/tasks"
        self.model_name = "Task"
