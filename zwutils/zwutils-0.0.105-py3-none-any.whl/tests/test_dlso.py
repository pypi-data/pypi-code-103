# -*- coding: utf-8 -*-
import pytest
import time

import zwutils.dlso as dlso

# pylint: disable=no-member
def test_dict2obj():
    r = dlso.dict2obj({
        'ks': 'v1',
        'kn': 2,
        'ka': [1, '2'],
        'kd': {'1':1, '2':2},
        'knone': None
    })
    r2 = dlso.dict2obj(None)
    assert r.ks == 'v1'

def test_obj2dict():
    o = type('', (), {})()
    o.a1 = 'a'
    o.a2 = 'b'
    r = dlso.obj2dict(o)
    assert r['a1'] == 'a'

def test_extend_attr():
    b = {'a':'a', 'b':'b'}
    e = {'b':'bb', 'c':'c', 'd':1}
    o = dlso.extend_attrs(dlso.dict2obj(b), e)
    assert o.b == 'bb' and o.c == 'c' and o.d == 1
    o = dlso.extend_attrs(b, e)
    assert o.b == 'bb' and o.c == 'c' and o.d == 1
    o = dlso.extend_attrs(dlso.dict2obj(b), dlso.dict2obj(e))
    assert o.b == 'bb' and o.c == 'c' and o.d == 1

    o = dlso.extend_attrs(None, e)
    assert o.b == 'bb' and o.c == 'c' and o.d == 1
    o = dlso.extend_attrs(dlso.dict2obj(b), None)
    assert o.a == 'a' and o.b == 'b'

def test_update_attrs():
    b = {'a':'a', 'b':'b'}
    e = {'b':'bb', 'c':'c'}
    o = dlso.update_attrs(dlso.dict2obj(b), e)
    assert o.b == 'bb' and not hasattr(o, 'c')
    o = dlso.update_attrs(b, e)
    assert o.b == 'bb' and not hasattr(o, 'c')
    o = dlso.update_attrs(dlso.dict2obj(b), dlso.dict2obj(e))
    assert o.b == 'bb' and not hasattr(o, 'c')

    o = dlso.update_attrs(None, e)
    assert not hasattr(o, 'b') and not hasattr(o, 'c')
    o = dlso.update_attrs(dlso.dict2obj(b), None)
    assert o.a == 'a' and o.b == 'b'

def test_upsert_config():
    pcfg = type('', (), {})()
    pcfg.a = 'o'
    dcfg = {'a': 'd', 'da':'da', 'n1':{'nn1': {'nnn1': 'nnn1'}, 'nn2': 'nn2' } }
    ncfg = {'a': 'n', 'na':'na'}
    pmcfg = {'a': 'p','pa':'pa'}
    cfg = dlso.upsert_config(pcfg, dcfg, ncfg, pmcfg)
    assert id(cfg) == id(pcfg) and cfg.a == 'p' and hasattr(cfg, 'pa') and cfg.n1.nn1.nnn1 == 'nnn1'
