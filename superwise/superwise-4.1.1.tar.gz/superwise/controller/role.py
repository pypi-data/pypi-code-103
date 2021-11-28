""" This module implement roles functionality  """
from superwise.controller.base import BaseController
from superwise.models.task import Task


class RoleController(BaseController):
    """ Role controller class, implement functionalitiws for roles API """

    def __init__(self, client, sw):
        """
        constructer for RoleController class

        :param client:

        """
        super().__init__(client, sw)
        self.path = "model/v1/roles"
        self.model_name = "Role"

    def list_to_dict(self, model_list):
        """
        change list of models into dict

        :param model_list: list of models
        :return dict
        """
        dict = {}
        for model in model_list:
            properties = model.get_properties()
            dict[properties["description"]] = properties
        return dict
