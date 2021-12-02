# -*- coding: utf-8 -*-
"""
Created on Sat Jun 29 22:34:51 2019

@author: jiangxue
"""

from crossref_commons.iteration import iterate_publications_as_json
from .data_archive import data_archive

def doi_catch():
    filter = {'prefix':'10.1016','type': 'journal-article'}#10.1016是Elsvier
    queries = {'query.bibliographic': {"alloys"}}
    doilist = []
    for p in iterate_publications_as_json(max_results=1000000, filter=filter, queries=queries):
        doilist.append(p['DOI'])
        print(p['DOI'])
        #data_archive(doilist,"doilist-doi.xlsx","doilist")
    return doilist

if __name__ == '__main__':
    doilist = doi_catch()
    data_archive(doilist,"alloyDOI.xlsx","alloyDOI")
