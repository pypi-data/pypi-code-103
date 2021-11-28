from gaelib.tests.base import BaseUnitTestCase
from gaelib.storage import helpers


class HelpersTestCase(BaseUnitTestCase):

  def setUp(self):
    super().setUp()

  def test_get_default_storage_bucket(self):
    self.assertEqual(helpers.get_default_storage_bucket(),
                     'codejedi-crypticcup-staging.appspot.com')

  def test_get_storage_bucket(self):
    self.assertEqual(helpers.get_storage_bucket(),
                     'codejedi-crypticcup-staging.appspot.com')
