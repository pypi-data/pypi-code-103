# -*- coding: utf-8 -*-
import pytest

from zwutils import mprocessing as mp

def multirun_cbfunc(s):
    return 'result: %s'%s

class TestMP:
    def test_multicmd(self):
        args = ['.', '/']
        cmds = [['ls', '-l', a] for a in args]
        r = mp.multiprocess_cmd(cmds)
        assert len(r) == len(args)
    
    def test_multirun(self):
        num = 10
        args = [(a,) for a in range(num)]
        r = mp.multiprocess_run(multirun_cbfunc, args)
        assert len(r) == num