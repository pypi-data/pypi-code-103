import os
from typing import Iterable
import re
from urllib.parse import urlparse


def _parsing(self):
    query_string = urlparse(self.next).query
    params = query_string.split('&')
    params_dict = dict()
    for param in params:
        tmp = param.split('=')
        params_dict[tmp[0]] = tmp[1]
    return params_dict


class QueryResult:
    def __init__(self,
                 limit: int = 1000,
                 next: str = '',
                 previous: str = '',
                 results: Iterable = list(),
                 start: int = 0,
                 total_count: int = 0,
                 ):
        self.limit = limit
        self.next = next
        self.previous = previous
        self.results = results
        self.start = start
        self.total_count = total_count
        self._cache = dict()

    def first(self):
        if not self.results:
            return None
        for item in self.results:
            return item

    def next_start(self):
        '''下一個起始數'''
        re_str = r'start=([0-9]+)'
        return int(re.search( re_str, self.next).group(1))

    def query_params(self, force=False):
        if force:
            params = _parsing()
            self._cache['query_params'] = params
            return self._cache['query_params']
        else:
            if self._cache.get('query_params'):
                return self._cache.get('query_params')
            params = _parsing()
            self._cache['query_params'] = params
            return self._cache['query_params']




# class QueryResult2:
#     def __init__(self, pmb_pagenation_query_result):
#         self._re = pmb_pagenation_query_result

#     @property
#     def results(self):
#         return self._re.results
    
#     @property
#     def next(self):
#         return self._re.next
    
#     @property
#     def previous(self):
#         return self._re.previous

#     @property
#     def start(self):
#         return self._re.start
    
#     @property
#     def limit(self):
#         return self._re.limit

#     @property
#     def total_count(self):
#         return self._re.total_count

#     def first(self):
#         if not self._re.results:
#             return None
#         for item in self._re.results:
#             return item

#     def next_start(self):
#         re_str = r'start=([0-9]+)'
#         return int(re.search( re_str, self._re.next).group(1))
