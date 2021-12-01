# This file is placed in the Public Domain.


import unittest


from bot.obj import dumps
from bot.run import Cfg
from bot.utl import getmain


class Test_Kernel(unittest.TestCase):

    def test_cfg(self):
        k = getmain("k")
        self.assertEqual(type(k.cfg), Cfg)

