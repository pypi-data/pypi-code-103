# pylint: skip-file
import os
from unittest.mock import MagicMock

from unimatrix.conf import settings
from unimatrix.lib.test import AsyncTestCase

from .. import __boot__ as boot


class SetupTestCase(AsyncTestCase):

    def setUp(self):
        self.settings = os.environ.pop('UNIMATRIX_SETTINGS_MODULE', None)
        settings.destroy()

    def tearDown(self):
        if self.settings is not None:
            os.environ['UNIMATRIX_SETTINGS_MODULE'] = self.settings

    async def test_on_setup_runs_without_settings(self):
        await boot.on_setup()
