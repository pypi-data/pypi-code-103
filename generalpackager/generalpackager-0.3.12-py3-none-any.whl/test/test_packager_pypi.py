

from generalpackager import Packager
from generalfile.test.setup_workdir import setup_workdir

import unittest


class TestPackager(unittest.TestCase):
    def test_get_latest_release(self):
        self.assertIn("CE", str(Packager().get_latest_release()))


