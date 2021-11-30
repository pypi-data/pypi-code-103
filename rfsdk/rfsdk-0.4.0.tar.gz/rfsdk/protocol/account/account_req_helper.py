# -*- coding: utf-8 -*-

def make_login_req(login, client_id='', qsid='', wtid=''):
    req = dict()
    req['client_id'] = client_id
    req['login'] = login
    req['qsid'] = qsid
    req['wtid'] = wtid

    return req


def make_logout_req(investor_key, client_id=''):
    req = dict()
    req['investor_key'] = investor_key
    req['client_id'] = client_id

    return req
