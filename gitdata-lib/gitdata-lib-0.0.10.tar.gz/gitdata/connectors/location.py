"""
    location connector
"""

# from .common import BaseConnector, get_connectors#, Source


# class LocationConnector(BaseConnector):

#     name = 'location'
#     reads = ['location']
#     writes = ['file', 'disk']

#     @property
#     def facts(self):
#         """Returns facts"""
#         print(list(x.__name__ for x in get_connectors()))
#         return dict(location='')


    # def _views(self, target):
    #     with open(target.pathname) as reader:
    #         return [
    #             Source('blob', reader)
    #         ]

    # def extract(self, source):
    #     with open(source.pathname) as reader:
    #         return reader

    # # legacy
    # def collect(self, target):
    #     with open(target.patname) as reader:
    #         return reader

