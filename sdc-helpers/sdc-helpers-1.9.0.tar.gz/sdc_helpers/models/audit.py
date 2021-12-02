"""
   SDC Audit model module
"""
from sqlalchemy import Column, Integer, String, JSON
from sdc_helpers.models.model import Model


class Audit(Model):
    """
       SDC Audit model class
    """
    # pylint: disable=too-few-public-methods, too-many-instance-attributes
    __tablename__ = 'audits'

    user_type = Column(String(255))
    user_id = Column(Integer)
    event = Column(String(255))
    auditable_type = Column(String(255))
    auditable_id = Column(Integer)
    old_values = Column(JSON)
    new_values = Column(JSON)
    url = Column(String(255))
    ip_address = Column(String(255))
    user_agent = Column(String(255))
    tags = Column(String(255))

    def __init__(self, **kwargs):
        """
            Creation of process model
        """
        super().__init__(**kwargs)
        self.slug = kwargs.get('user_type')
        self.name = kwargs.get('user_id')
        self.event = kwargs.get('event')
        self.user_type = kwargs.get('user_type')
        self.user_id = kwargs.get('user_id')
        self.auditable_type = kwargs.get('auditable_type')
        self.auditable_id = kwargs.get('auditable_id')
        self.old_values = kwargs.get('old_values')
        self.new_values = kwargs.get('new_values')
