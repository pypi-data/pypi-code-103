

from generalpackager import Packager
from generalfile.test.setup_workdir import setup_workdir

import unittest


class TestPackager(unittest.TestCase):
    """ Skipped:
        spawn_children
        spawn_parents
        """
    def test_exists(self):
        self.assertEqual(True, Packager().exists())




