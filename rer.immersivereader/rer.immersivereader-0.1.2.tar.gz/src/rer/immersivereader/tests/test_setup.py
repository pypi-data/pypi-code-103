# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID
from rer.immersivereader.testing import (
    RER_IMMERSIVEREADER_INTEGRATION_TESTING  # noqa: E501,
)

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that rer.immersivereader is properly installed."""

    layer = RER_IMMERSIVEREADER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if rer.immersivereader is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'rer.immersivereader'))

    def test_browserlayer(self):
        """Test that IRerImmersivereaderLayer is registered."""
        from rer.immersivereader.interfaces import (
            IRerImmersivereaderLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IRerImmersivereaderLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = RER_IMMERSIVEREADER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['rer.immersivereader'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if rer.immersivereader is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'rer.immersivereader'))

    def test_browserlayer_removed(self):
        """Test that IRerImmersivereaderLayer is removed."""
        from rer.immersivereader.interfaces import \
            IRerImmersivereaderLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IRerImmersivereaderLayer,
            utils.registered_layers())
