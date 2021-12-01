from sqlalchemy import Column, Integer

from .func_date import get_timestamp_now


class BaseModal:
    created_at = Column(Integer, server_default=str(get_timestamp_now()))
    updated_at = Column(Integer, server_default=str(get_timestamp_now()))
