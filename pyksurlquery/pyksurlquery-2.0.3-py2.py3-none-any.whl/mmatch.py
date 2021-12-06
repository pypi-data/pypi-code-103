#! /usr/bin/python
# coding: UTF-8
import chardet
from ctypes import *
from .urltype_def import *
from .udmurl import udmurlmatch

try:
    libmatch_lib = cdll.LoadLibrary('liburlmatch.so')
except OSError as e:
    libmatch_lib = None


def mmatch(url):
    ret = {}

    urltype = c_int(4)
    purltype = pointer(urltype)
    eviltype = c_int(4)
    peviltype = pointer(eviltype)
    domaintype = c_int(4)
    pdomaintype = pointer(domaintype)

    # just in case
    if not isinstance(url, str):
        # noinspection PyBroadException
        try:
            f_encoding = chardet.detect(url)
            url = url.decode(f_encoding['encoding'])
        except Exception:
            return None

    res = udmurlmatch(url)
    if res:
        return res

    if not libmatch_lib:
        return None

    url = url.encode('utf-8')
    res = libmatch_lib.match_murl_web(url, len(url), purltype, peviltype, pdomaintype)
    if res != 0:
        return None

    ut = urltype.value
    et = eviltype.value
    dt = domaintype.value

    if ut == 2:
        ret['urltype'] = ut
        ret['eviltype'] = et
        ret['domaintype'] = True if dt else False  # ternary

        load_eviltypes_if_modified()
        if et in get_eviltype_dict():
            ret['desc'] = get_eviltype_desc(et)
            ret['action_block'] = get_eviltype_action(et)
            ret['classification'] = get_classification(et)
        else:
            ret = None

        return ret
    else:
        return None


def mmurladd(url, level, url_type):
    url = url.encode('utf-8')
    res = libmatch_lib.add_curtom_murl(url, level, url_type)

    if res == -1:
        print('bad input')
    elif res == -2:
        print('memory full')

    return res


def mmurldel(url, level):
    url = url.encode('utf-8')
    res = libmatch_lib.del_custom_murl(url, level)

    if res == -1:
        print('bad input')
    elif res == -2:
        print('memory full')

    return res


def testcase1():
    url = u'http://119.11042110.com'
    r = mmatch(url)
    print(r)
    r = mmatch('www.baidu.com/abc.html')
    r = mmatch('www.sina.com')
    r = mmatch('testhelixli.com/index.html')
    r = mmatch('home.188lu.us')
    r = mmatch('www.kuaichatong.com')
    r = mmatch('tbcgd.cc')
    url = u'bencerpaow.cc'
    r = mmatch(url)


if __name__ == '__main__':
    testcase1()

