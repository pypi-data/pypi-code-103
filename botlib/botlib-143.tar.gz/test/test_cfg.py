# This file is placed in the Public Domain.

import unittest

from bot.obj import Object, update
from bot.ofn import edit
from bot.prs import parse


cfg = Object()


class Test_Cfg(unittest.TestCase):
    def test_parse(self):
        parse(cfg, "m=irc")
        self.assertEqual(cfg.sets.m, "irc")

    def test_parse2(self):
        parse(cfg, "m=irc,rss")
        self.assertEqual(cfg.sets.m, "irc,rss")

    def test_edit(self):
        d = Object()
        update(d, {"m": "irc,rss"})
        edit(cfg, d)
        self.assertEqual(cfg.m, "irc,rss")
