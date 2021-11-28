# -*- coding: utf-8 -*-
import pytest
import time

import zwutils.comm as comm

# pylint: disable=no-member
def test_dict2attr():
    r = comm.dict2attr({
        'ks': 'v1',
        'kn': 2,
        'ka': [1, '2'],
        'kd': {'1':1, '2':2},
        'knone': None
    })
    r2 = comm.dict2attr(None)
    assert r.ks == 'v1'

def test_attr2dict():
    o = type('', (), {})()
    o.a1 = 'a'
    o.a2 = 'b'
    r = comm.attr2dict(o)
    assert r['a1'] == 'a'

def test_extend_attr():
    b = {'a':'a', 'b':'b'}
    e = {'b':'bb', 'c':'c', 'd':1}
    o = comm.extend_attrs(comm.dict2attr(b), e)
    assert o.b == 'bb' and o.c == 'c' and o.d == 1
    o = comm.extend_attrs(b, e)
    assert o.b == 'bb' and o.c == 'c' and o.d == 1
    o = comm.extend_attrs(comm.dict2attr(b), comm.dict2attr(e))
    assert o.b == 'bb' and o.c == 'c' and o.d == 1

    o = comm.extend_attrs(None, e)
    assert o.b == 'bb' and o.c == 'c' and o.d == 1
    o = comm.extend_attrs(comm.dict2attr(b), None)
    assert o.a == 'a' and o.b == 'b'

def test_update_attrs():
    b = {'a':'a', 'b':'b'}
    e = {'b':'bb', 'c':'c'}
    o = comm.update_attrs(comm.dict2attr(b), e)
    assert o.b == 'bb' and not hasattr(o, 'c')
    o = comm.update_attrs(b, e)
    assert o.b == 'bb' and not hasattr(o, 'c')
    o = comm.update_attrs(comm.dict2attr(b), comm.dict2attr(e))
    assert o.b == 'bb' and not hasattr(o, 'c')

    o = comm.update_attrs(None, e)
    assert not hasattr(o, 'b') and not hasattr(o, 'c')
    o = comm.update_attrs(comm.dict2attr(b), None)
    assert o.a == 'a' and o.b == 'b'

def test_contains_digits():
    assert comm.contains_digits('aaabb, 332 44 -adaf')
    assert not comm.contains_digits('aaabb,-adaf')

def test_print_duration():
    @comm.print_duration
    def test_func():
        for i in range(3):
            time.sleep(1)
    test_func()
    assert 1

def test_list_split():
    r = comm.list_split(list(range(11)), 3)
    assert len(r) == 3
    r = comm.list_split(list(range(5)), 6)
    assert len(r) == 5

def test_list_compare():
    assert False == comm.list_compare([1,2,3,3], [1,2,2,3])
    assert True == comm.list_compare([1,2,3], [2,1,3])

def test_upsert_config():
    cfg = comm.dict2attr({'fld1':1, 'fld2':'b'})
    r = comm.upsert_config(cfg, {'fld2':'bb', 'fld3':'cc'}, {'fld2':'z', 'fld4':4})
    assert r.fld1 == 1 and r.fld2 == 'bb' and r.fld3 == 'cc' and r.fld4 == 4

    r = comm.upsert_config(None, {'fld2':'bb', 'fld3':'cc'}, {'fld2':'z', 'fld4':4})
    assert r.fld2 == 'bb' and r.fld3 == 'cc' and r.fld4 == 4

    r = comm.upsert_config(None, {'fld2':'bb', 'fld3':'cc'})
    assert r.fld2 == 'bb' and r.fld3 == 'cc'

    cfg = comm.dict2attr({'fld1':1, 'fld2':'b'})
    r = comm.upsert_config(cfg, def_val={'fld2':'z', 'fld4':4})
    assert r.fld2 == 'b' and r.fld4 == 4

    cfg = comm.dict2attr({'fld1':1, 'fld2':'b'})
    r = comm.upsert_config(cfg, {}, {'fld':'abc', 'flddict': {'a1':1, 'a2':'b'}})
    assert r.flddict.a1 == 1