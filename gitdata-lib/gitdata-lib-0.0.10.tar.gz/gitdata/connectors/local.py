"""
    local filesystem connector
"""


from .common import BaseConnector


class FileConnector(BaseConnector):

    name = 'file'
    reads = ['location']
    writes = ['text', 'blob', 'stdout']

    # def explore(self, data):
    #     """Explore Data"""
    #     print('exploring location', data)


class DirectoryConnector(BaseConnector):

    name = 'directory'
    reads = ['location']
    writes = ['location']


#     def _views(self, target):
#         with open(target.pathname) as reader:
#             return [
#                 Source('blob', reader)
#             ]

#     def extract(self, source):
#         with open(source.patname) as reader:
#             return reader

#     # legacy
#     def collect(self, target):
#         with open(target.patname) as reader:
#             return reader

