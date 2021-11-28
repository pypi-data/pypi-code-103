# -*- coding: utf-8 -*-
from iTesting.main import TestMark


class Demo:
    @staticmethod
    def login(username, password):
        # 这里写你的业务逻辑，简单起见，我返回True
        print('\n%s' % username)
        print('\n%s' % password)
        return True


class TestDemo:
    def test_login(self, username, password, expected):
        assert Demo.login(username, password) == expected

    @TestMark('myMark')
    def test_demo_true(self):
        assert True

    def test_demo_false(self):
        assert False

