#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def parametrized(dec):
    """데코레이터에 파라미터 입력하는 데코레이터"""

    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)

        return repl

    return layer


@parametrized
def types(function, *types):
    """타입 제한 데코레이터"""

    def rep(*args, **kwargs):
        for a, t, n in zip(args, types, itertools.count()):
            if type(a) is not t:
                raise TypeError('Value %d has not type %s. %s instead' % (n, t, type(a)))
        return function(*args, **kwargs)

    return rep
