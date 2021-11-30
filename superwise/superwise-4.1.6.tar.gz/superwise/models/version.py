""" This module implement version  model  """
import pandas as pd

from superwise.models.base import BaseModel


class Version(BaseModel):
    """ Version model class, model  for version data """

    def __init__(
        self,
        id=None,
        task_id=None,
        name=None,
        created_at=None,
        baseline_files=None,
        data_entities=None,
        baseline_df=None,
        status=None,
        **kwargs
    ):
        """
        constructor for Version class

        :param task_id:
        :param name:
        :param client_name:
        :param external_id:
        :param created_at:
        :param baseline_files:
        :param data_entities:
        """
        self.id = id
        self.task_id = task_id
        self.name = name
        self.created_at = created_at
        self.data_entities = data_entities or []
        self.baseline_files = baseline_files or []
        self.status = status
        self.baseline_df = baseline_df
