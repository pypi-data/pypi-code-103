"""
    rows connector
"""


from .common import BaseConnector


class RowsConnector(BaseConnector):
    """Rows Connector"""

    name = 'console'
    reads = ['rows']
    writes = ['text']

