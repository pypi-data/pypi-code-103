#!/usr/bin/env python
# coding=utf-8

import requests
from urllib.parse import urlparse
import csv
import warnings
from .urltype_def import *
from .settings import AUTH_URL, BW_URL, USERNAME, PASSWORD, BLACKLIST_FILE, TOKEN_FILE

try:
    from afwfcfg import black_white_list as bwl
except ImportError as e:
    warnings.warn('bwl do not be imported')


LFTIMESTAMP = 0
BLACKLIST_DICT = {}
INIT_DONE = False


# url must be unicode
def udmurlmatch(url):
    global LFTIMESTAMP

    if not os.path.isfile(BLACKLIST_FILE):
        return

    if not isinstance(url, str):
        return

    # to check current file timestamp
    cftimestamp = os.path.getmtime(BLACKLIST_FILE)
    if cftimestamp != LFTIMESTAMP:
        # clear black list dict when the data is changed
        BLACKLIST_DICT.clear()
        # read blacklist file , and get new blacklist dict
        with open(BLACKLIST_FILE, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                murl = row[0].encode().decode('utf-8').strip('/')
                value = {}
                value['eviltype'] = int(row[1].encode().decode('utf-8'))
                value['domaintype'] = True
                BLACKLIST_DICT[murl] = value
        LFTIMESTAMP = cftimestamp

    protocol = "http"
    if url.startswith(f'{protocol}://'):
        domain = urlparse(url).netloc
    else:
        domain = urlparse(f'{protocol}://{url}').netloc
    complete_domain = f'{protocol}://{domain}'

    value = None
    if url in BLACKLIST_DICT:
        value = BLACKLIST_DICT[url]
    elif complete_domain in BLACKLIST_DICT:
        value = BLACKLIST_DICT[complete_domain]

    ret = None
    if value:
        ret = {
            'urltype': 2,
            'eviltype': value['eviltype'],
            'desc': get_eviltype_desc(value['eviltype']),
            'domaintype': value['domaintype'],
            'action_block': get_eviltype_action(value['eviltype'])
        }
    return ret


def add_url(typ, url, scope):
    if 'bwl' not in globals():
        return

    url = url.encode('utf-8')

    if typ == 'black':
        if bwl.BLACK_URL_AddWithLevel(url, scope) != 0:
            return False
    elif typ == 'white':
        if bwl.WHITE_URL_AddWithLevel(url, scope) != 0:
            return False

    return True


def bw_record_sync():
    if 'bwl' not in globals():
        return

    global INIT_DONE
    if not INIT_DONE:
        if not bwl.BlackWhiteInit():
            INIT_DONE = True
        else:
            return

    # get bwlist from tmp file
    bw_dict = {}

    if os.path.isfile(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, 'r') as f:
            csvreader = csv.reader(f)
            for row in csvreader:
                # decode to unicode
                bw_dict[row[0].encode().decode('utf-8')] = row[2].encode().decode('utf-8')

    # get auth token
    # if access_file is not exist, use username and password login
    if os.path.isfile(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as fp:
            token = fp.read()
        headers = {
            'Authorization': 'TOKEN ' + token
        }
    else:
        data = {'username': USERNAME, 'password': PASSWORD}
        authtoken = requests.post(AUTH_URL, data, verify=False)
        token = json.loads(authtoken.text)['token']

        headers = {
            'Authorization': 'JWT ' + token
        }

    # get bwlist from db
    all_list = []
    bwlist = requests.get(BW_URL, headers=headers, verify=False)
    response = json.loads(bwlist.text)
    result = response['results']
    all_list.extend(result)
    while response['next']:
        bwlist = requests.get(response['next'], headers=headers, verify=False)
        response = json.loads(bwlist.text)
        result = response['results']
        all_list.extend(result)

    # 如果 count 相等，则走下面路径
    with open(BLACKLIST_FILE, 'w') as f:
        csvwriter = csv.writer(f)
        for r in all_list:
            # records do not need del
            if r['url'] in bw_dict:
                # overwrite the bw record
                if r['type'] != bw_dict[r['url']]:
                    # do not write file when add url fail
                    if not add_url(r['type'], r['url'], r['scope']):
                        continue

                del bw_dict[r['url']]
            # new records
            else:
                # do not write file when add url fail
                if not add_url(r['type'], r['url'], r['scope']):
                    continue

            # write bw record into tmp file
            # write to file as binary
            csvwriter.writerow((
                r['url'].encode('utf-8'),
                # if it is a white record use default 0
                r['eviltype'] or 0,
                r['type'].encode('utf-8')
            ))

    for url, typ in bw_dict.items():
        if typ == 'black':
            bwl.BLACK_URL_Del(url.encode('utf-8'))
        elif typ == 'white':
            bwl.WHITE_URL_Del(url.encode('utf-8'))


if __name__ == '__main__':
    bw_record_sync()
