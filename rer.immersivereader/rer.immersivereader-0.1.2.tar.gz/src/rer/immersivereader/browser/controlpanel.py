# -*- coding: utf-8 -*-
# from plone.z3cform import layout
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from rer.immersivereader.interfaces import IImmersiveReaderSettings
from rer.immersivereader import _


class SettingsEditForm(RegistryEditForm):
    """Define form logic"""

    schema = IImmersiveReaderSettings
    schema_prefix = "rer.immersivereader"
    label = _(u"Immersive Reader Settings")


class SettingsView(ControlPanelFormWrapper):
    """Control Panel form wrapper"""

    form = SettingsEditForm
