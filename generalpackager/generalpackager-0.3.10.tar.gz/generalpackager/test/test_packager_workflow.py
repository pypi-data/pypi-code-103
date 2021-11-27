

from generalpackager import Packager
from generalfile.test.setup_workdir import setup_workdir

import unittest


class TestPackager(unittest.TestCase):
    """ Skipped:
        workflow_unittest
        workflow_sync
        if_publish_bump
        if_publish_publish
        """
    def test_get_triggers(self):
        self.assertIn("branches", Packager().get_triggers())

    def test_step_setup_python(self):
        self.assertIn("3.8", Packager().step_setup_python("3.8"))

    def test_step_install_necessities(self):
        self.assertIn("pip install", Packager().step_install_necessities())

    def test_step_install_package_pip(self):
        self.assertIn("pip install", Packager().step_install_package_pip(*Packager().get_ordered_packagers()))

    def test_step_install_package_git(self):
        self.assertIn("pip install git", Packager().step_install_package_git(*Packager().get_ordered_packagers()))

    def test_get_env(self):
        self.assertIn("TWINE", Packager().get_env())

    def test_steps_setup(self):
        self.assertIn("pip install", Packager().steps_setup("3.8"))

    def test_get_unittest_job(self):
        self.assertIn("pip install", Packager().get_unittest_job())

    def test_get_sync_job(self):
        self.assertIn("pip install", Packager().get_sync_job())

    def test_step_run_packager_method(self):
        self.assertIn("Packager(", Packager().step_run_packager_method("foo"))

    def test_run_ordered_methods(self):
        x = []
        def a(_): x.append(1)
        def b(_): x.append(2)
        Packager().run_ordered_methods(a, b)
        length = len(Packager().get_all())
        self.assertEqual([1] * length + [2] * length, x)

