"""
    system connector
"""

import platform
import datetime

from .common import BaseConnector


class System(BaseConnector):

    # def connects(self, ref):
    #     return ref == 'system'

    def connect(self, ref):
        pass

    @property
    def name(self):
        return platform.node()

    @property
    def date(self):
        return datetime.date.today()

    @property
    def time(self):
        return datetime.datetime.now()
