#! /usr/bin/python
# coding: UTF-8
import os
import json
import codecs

from .settings import EVILTYPES_FILE, EVILTYPES_ACTION_FILE


EVILTYPES_DICT = {}
EVILTYPES_ACTION_DICT = {}
CLASSIFICATION_DICT = {}
TYPESFILE_TIMESTAMP = 0
ACTIONFILE_TIMESTAMP = 0


def load_eviltypes_if_modified():
    # update this var if modified
    global TYPESFILE_TIMESTAMP
    global EVILTYPES_DICT
    if not os.path.isfile(EVILTYPES_FILE):
        return
    cftimestamp = os.path.getmtime(EVILTYPES_FILE)
    if cftimestamp != TYPESFILE_TIMESTAMP:
        with codecs.open(EVILTYPES_FILE, 'r', encoding='utf-8') as fp:
            templist = json.load(fp, encoding='utf-8')
            for item in templist:
                EVILTYPES_DICT[item.get('eviltype')] = item
                c = item.get('classification')
                if c not in CLASSIFICATION_DICT:
                    CLASSIFICATION_DICT[c] = item.get('classification_name')
        TYPESFILE_TIMESTAMP = cftimestamp


def load_action_if_modified():
    # update this var if modified
    global ACTIONFILE_TIMESTAMP
    global EVILTYPES_ACTION_DICT
    if not os.path.isfile(EVILTYPES_ACTION_FILE):
        return
    cftimestamp = os.path.getmtime(EVILTYPES_ACTION_FILE)
    if cftimestamp != ACTIONFILE_TIMESTAMP:
        with codecs.open(EVILTYPES_ACTION_FILE, 'r', encoding='utf-8') as fp:
            EVILTYPES_ACTION_DICT = json.load(fp, encoding='utf-8')
        ACTIONFILE_TIMESTAMP = cftimestamp


def get_eviltype_desc(eviltype):
    load_eviltypes_if_modified()
    if eviltype in EVILTYPES_DICT:
        desc = EVILTYPES_DICT[eviltype]['wording_body']
    else:
        desc = '此网站曾被识别有恶意元素，建议您谨慎访问。'
    return desc


def get_evil_desc(eviltype):
    load_eviltypes_if_modified()
    if eviltype in EVILTYPES_DICT:
        desc = EVILTYPES_DICT[eviltype]['evil_desc']
    else:
        desc = '恶意网址'
    return desc


def get_eviltype_action(eviltype):
    load_action_if_modified()
    return eviltype in EVILTYPES_ACTION_DICT


def get_classification(eviltype):
    load_eviltypes_if_modified()
    if eviltype in EVILTYPES_DICT:
        classification = EVILTYPES_DICT[eviltype]['classification']
    else:
        classification = 0
    return classification


def get_eviltype_dict():
    load_eviltypes_if_modified()
    return EVILTYPES_DICT


def get_classification_dict():
    load_eviltypes_if_modified()
    return CLASSIFICATION_DICT


if __name__ == '__main__':
    print(get_eviltype_desc(2))
    print(get_eviltype_action(2))
    print(get_classification(2))
    print(get_eviltype_dict())

