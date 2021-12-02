"""
   SDC Service model module
"""
from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.orm import relationship
from sdc_helpers.models.model import Model
from sdc_helpers.models.subscription import Subscription


class Service(Model):
    """
       SDC Service model class
    """
    # pylint: disable=too-few-public-methods
    __tablename__ = 'services'

    slug = Column(String(255), unique=True)
    name = Column(String(255))
    properties = Column(JSON)
    updated_by = Column(String(255))
    deleted_at = Column(DateTime)
    subscriptions = relationship(Subscription)

    def __init__(self, **kwargs):
        """
            Creation of service model
        """
        super().__init__(**kwargs)
        self.slug = kwargs.get('slug')
        self.name = kwargs.get('name')
