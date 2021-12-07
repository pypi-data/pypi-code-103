#!/usr/bin/env python
# -*- coding: utf8 -*-
import pytz
import requests


import sys
import pathlib

here = pathlib.Path(__file__)
sys.path.append(str(here.parent.parent))
# from PyFileMaker import FMServer as OldFm

from pyfilemaker2 import FmServer, FmError
import sys
import time
# code

# import modules

import time

# class appointment:
#     def __init__(self):
#         self.data = queue.Queue()
#         self.ended = False

#     # def consummer(self):
#     #     while True:
#     #         condition_object.acquire()
#     #         print("Consummer has job")
#     #         if self.ended:
#     #             print("Got end signal")
#     #             break
#     #         if self.data.empty():
#     #             condition_object.wait() # Thread is in waiting state
#     #             if self.ended:
#     #                 print("Got end signal")
#     #                 break
#     #         item = self.data.get()
#     #         print("GOT", item)
#     #         condition_object.release()
#     #         time.sleep(0.1)

#     def producer(self):
#         for i in range(10):
#             condition_object.acquire()
#             time.sleep(.1)
#             self.data.put(i)
#             print(f"Pushed {i} into queue")
#             condition_object.notify()
#             condition_object.release()
#             time.sleep(1)

#         condition_object.acquire()
#         print("Signify end of job.")
#         self.ended = True
#         condition_object.notify()
#         condition_object.release()


# condition_object = Condition()
# class_obj=appointment()

# T1 = Thread(target=class_obj.producer)

# # T2 = Thread(target=class_obj.consummer)


# T1.start() # will start and will starts fill self.data

# def test():
#     while True:
#         condition_object.acquire()
#         if class_obj.ended and class_obj.data.empty():
#             return
#         if class_obj.data.empty():
#             condition_object.wait() # Thread is in waiting state
#             if class_obj.ended and class_obj.data.empty():
#                 return
#         item = class_obj.data.get()
#         condition_object.release()
#         yield item

# for ii in test():
#     print("GOT", ii)
#     time.sleep(1.5)

# # T2.start()

# sys.exit(0)
# u = "https://10.242.155.14:443/fmi/xml/fmresultset.xml?-db=TestJeremie&-lay=test_table_query&id=1&-lop=and&-find="
# u = "https://essaim-norma.etat-de-vaud.ch:443/fmi/xml/fmresultset.xml?-db=TestJeremie&-lay=test_table_query&id=1&-lop=and&-find="
# # user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36'
# # headers = {'User-Agent': user_agent}

# r = requests.get( u, auth=('xml', 'xml1234'), verify=True, stream=True, timeout=1 )
# r.raise_for_status()
# print( "***", r.raw.read(), "***" )

# print(r.headers)

# class A(object):
#     class Option:
#         toto = 22

#     def test(self):
#         print( self.__class__.Option.toto )

#     @classmethod
#     def ctest(cls):
#         print( cls.Option.toto )

# class B(A):
#     class Option:
#         toto = 34

#     def __init__( self):
#         setattr( self.__class__.Option, 'toto', 42 )

# a = B()
# a.test()
# B.ctest()

# # sys.exit(0)

# import urllib3
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# https://xml:xml1234@essaim-norma.etat-de-vaud.ch/fmi/xml/fmresultset.xml?-db=TestJeremie&-lay=tableB&-findall
# url = "https://xml:xml1234@essaim-norma.etat-de-vaud.ch/fmi/xml/fmresultset.xml?-db=TestJeremie&-lay=layout1&-findall"
# response = requests.get(url, stream=True, timeout=60 )
# s = pyfilemaker2.parser.parse(
#     stream=response.raw
# )


z = pytz.timezone('Europe/Zurich')

from pyfilemaker2.caster import FM_NUMBER, CommaDecimalNumberCast, NumberCast



class MyFm(FmServer):
    # aiohttp_kwargs={
    #     'timeout': 15,
    #     'stream': True,
    #     'verify': True,
    # }
    server_timezone = z
    


# fm = OldFm(
fm = MyFm(
    url='https://xml:xml1234@essaim-norma.dfj.vd.ch',
    debug=True,
    db='TestFile',
    layout='table2',
    threaded_paginate=True,
    cast_map = { FM_NUMBER: CommaDecimalNumberCast }
)
t1 = time.monotonic()
# fm.do_script('generate_dummy_data', param=100000, return_all=False)
# sys.exit(1)
titi = []
for k, item in enumerate(fm.do_find_all(paginate=10000)):
    print(item)

t2 = time.monotonic()
print("time is ", t2-t1)
sys.exit(0)

item = item[0]

item['f_multi_text(2)'] = 'nouveau'

fm.do_edit(item)


print(item)
print("DONE")

# item['dataC'] = """Salut les pôtes ~~~~~été ßß

# Qud diriez-vous d'un apéro ?
# """

# result = fm.do_script( script_name='generate_dummy_data', param=22000, return_all=False )
# tuple(result)

# print( "AAAAA", fm.total_records_number(), fm.fetched_records_number() )

# res = fm.doFindQuery({
# res = fm.do_find_query(OrderedDict([
#     ('2',{'datac':'data'}),
#     ('1',{'idc': '2', 'datac':'data2'}),
#     ('3',{'datac':'zata'}),
#     ]),
#     sort=['-datac']
# )

# for item in results:
#     print("***", item)
# print(res)

# https://essaim-norma.etat-de-vaud.ch:443/fmi/xml/fmresultset.xml?-db=TestJeremie&-lay=table1&
# -query=(q1);(q2);!(q3);(q4);(q5);(q6);(q7)
# -q1=color&-q1.value=red&-q2=color&-q2.value=blue&-q3=gender&-q3.value=m&-q4=
# id&-q4.value=1&-q5=id&-q5.value=2&-q6=id&-q6.value=3&-q7=id&-q7.value=4&
# -findquery

# for item in res:
#     print(item['r1'])

# f = open( './tests/ressources/dbnames.xml', 'r' )
# s = pyfilemaker2.parser.parse(
#     stream=f,
#     fm_meta=meta,
#     only_meta=False,
# )

# for item in s:
#     print(item)

# print(meta.dump())

#print( response)

# print( s.dump() )
