from gaelib.tests.base import BaseUnitTestCase
from gaelib.db import helpers


class HelpersTestCase(BaseUnitTestCase):

  def setUp(self):
    super().setUp()

  def test_datastore_namespace(self):
    self.assertEqual(helpers.get_datastore_namespace(), 'DEFAULT')
