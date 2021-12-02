"""
   SDC Process model module
"""
from sqlalchemy import Column, String, DateTime
from sdc_helpers.models.model import Model


class Process(Model):
    """
       SDC Process model class
    """
    # pylint: disable=too-few-public-methods
    __tablename__ = 'processes'

    slug = Column(String(255), unique=True)
    name = Column(String(255))
    deleted_at = Column(DateTime)

    def __init__(self, **kwargs):
        """
            Creation of process model
        """
        super().__init__(**kwargs)
        self.slug = kwargs.get('slug')
        self.name = kwargs.get('name')
