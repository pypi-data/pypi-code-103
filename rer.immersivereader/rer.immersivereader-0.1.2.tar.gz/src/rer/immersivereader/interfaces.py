# -*- coding: utf-8 -*-
from rer.immersivereader import _
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.schema import List, Choice


class IRerImmersivereaderLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IImmersiveReaderSettings(Interface):
    """ """

    enabled_types = List(
        title=_(u"enabled_types_label", default=u"Enabled portal types"),
        description=_(
            u"enabled_types_help",
            default=u"Select a list of portal types that will have Immersive Reader link enabled.",
        ),
        required=True,
        default=[],
        missing_value=[],
        value_type=Choice(vocabulary="plone.app.vocabularies.PortalTypes"),
    )
