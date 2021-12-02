"""
   SDC Client model module
"""
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.orm import relationship
from sdc_helpers.models.model import Model
from sdc_helpers.models.subscription import Subscription

class Client(Model):
    """
       SDC Client model class
    """
    # pylint: disable=too-few-public-methods
    __tablename__ = 'clients'

    code = Column(String(255), unique=True)
    name = Column(String(255))
    properties = Column(JSON)
    deleted_at = Column(DateTime)
    updated_by = Column(String(255))
    subscriptions = relationship(Subscription)

    def __init__(self, **kwargs):
        """
            Creation of client model
        """
        super().__init__(**kwargs)
        self.code = kwargs.get('code')
        self.name = kwargs.get('name')
        self.last_login_at = self.convert_json_datetime(kwargs.get('last_login_at'))
