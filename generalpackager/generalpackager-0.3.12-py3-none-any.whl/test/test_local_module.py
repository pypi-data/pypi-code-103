
from generalpackager.api.local_module import LocalModule

import unittest


class TestLocalModule(unittest.TestCase):
    """ Skipped tests:
    """
    def test_exists(self):
        self.assertEqual(True, LocalModule("generalpackager").exists())
        self.assertEqual(False, LocalModule("doesntexist").exists())

    def test_module(self):
        self.assertEqual("generalpackager", LocalModule().module.__name__)

    def test_objInfo(self):
        self.assertLess(10, len(LocalModule().objInfo.get_children(depth=-1)))

    def test_get_env_vars(self):
        self.assertGreater(len(LocalModule().get_env_vars()), 1)

    def test_get_all_local_modules(self):
        self.assertIn(LocalModule("generallibrary"), LocalModule().get_all_local_modules())
        self.assertIn(LocalModule("generalfile"), LocalModule().get_all_local_modules())
        self.assertNotIn(LocalModule("doesntexist"), LocalModule().get_all_local_modules())

    def test_get_dependencies(self):
        self.assertIn(LocalModule("generallibrary"), LocalModule().get_dependencies())
        self.assertIn(LocalModule("generalfile"), LocalModule().get_dependencies())
        self.assertNotIn(LocalModule("doesntexist"), LocalModule().get_dependencies())

    def test_get_dependants(self):
        self.assertEqual([], LocalModule().get_dependants())







