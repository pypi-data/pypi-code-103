"""
Sistamapy - Simple statuses Mastodon for Python
Copyright (C) 2020 Vitor Guia

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import unittest
from time import time
from os import environ
from sepbit.sistamapy.statuses import Statuses

class StatusesTest(unittest.TestCase):
    """
    Test statuses.py module
    """
    toot_id = 0

    def setUp(self):
        '''
        Set credentials
        '''
        self.toot = Statuses(
            environ['INSTANCE'],
            environ['TOKEN']
        )


    def test_01_post(self):
        """
        Test post method
        """
        post = self.toot.post({
            'status': 'test ' + str(time()),
            'language': 'por',
            'visibility': 'public'
        })

        self.__class__.toot_id = post['id']
        self.assertTrue(post)


    def test_02_get(self):
        """
        Test get method
        """
        get = self.toot.get(
            self.__class__.toot_id
        )

        self.assertTrue(get)


    def test_03_delete(self):
        """
        Test delete method
        """
        delete = self.toot.delete(
            self.__class__.toot_id
        )

        self.assertTrue(delete)


if __name__ == '__main__':
    unittest.main()
