"""
    local filesystem connector
"""


from .common import BaseConnector


class ZipConnector(BaseConnector):

    name = 'zip'
    reads = ['blob']
    writes = ['blob']

    def explore(self, data):
        """Explore Data"""
        print('zip exploring blob')


