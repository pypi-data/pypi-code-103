#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: wxnacy(wxnacy@gmail.com)
# Description:

import unittest
from wpy import base

CONTENT = 'wxnacy'

class User(base.BaseObject):
    id = 0
    name = None

class TestCase(unittest.TestCase):
    def setUp(self):
        pass
    def teardown(self):
        pass

    def test_base_object(self):
        user = User(id=1, name='wxnacy')
        self.assertEqual(1, user.id)
        self.assertEqual('wxnacy', user.name)
        user_dict = user.to_dict()
        self.assertEqual(1, user_dict['id'])
        self.assertEqual('wxnacy', user_dict['name'])

if __name__ == "__main__":
    unittest.main()
