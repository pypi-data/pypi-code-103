""" This module implement Task model  """
from superwise.models.base import BaseModel


class Task(BaseModel):
    """ Task model class, model  for tasks data """

    def __init__(
        self,
        id=None,
        external_id=None,
        name=None,
        description=None,
        monitor_delay=None,
        time_units=None,
        is_archive=None,
        **kwargs
    ):
        """
        constructer for Task class
        :param id:
        :param external_id:
        :param name:
        :param description:
        :param monitor_delay:
        :param time_units:
        :param is_archive:
        """
        self.external_id = external_id
        self.name = name
        self.id = id or None
        self.description = description
        self.monitor_delay = monitor_delay
        self.time_units = time_units
        self.is_archive = is_archive
