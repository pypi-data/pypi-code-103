# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals, print_function
# from xyz_util.crawlutils import http_get
from xyz_util.datautils import access
# from base64 import encodestring
import requests

#
# def get_sina_short_url(url):
#     r = http_get('https://sina.lt')
#     bs = encodestring(url)
#     r = http_get('https://sina.lt/api.php?from=w&url=%s&site=t.hk.uy' % bs, cookies=r.cookies)
#     return r


def get_location_address(longitude, latitude):
    from django.conf import settings
    ak = access(settings, 'BAIDU.MAP.AK')
    url = 'https://api.map.baidu.com/reverse_geocoding/v3/?ak=%s&output=json&coordtype=wgs84ll&location=%s,%s' % (
    ak, latitude, longitude)
    r = requests.get(url)
    d = r.json()
    l = access(d, 'result.addressComponent')
    return "{province}{city}{district}{street}{street_number}".format(**l)
