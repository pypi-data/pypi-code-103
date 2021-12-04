#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_zfiles.zmi.synchronizer module

This module defines management views for synchronization utility.
"""

from pyams_form.field import Fields
from pyams_form.interfaces.form import IInnerSubForm
from pyams_form.subform import InnerEditForm
from pyams_utils.adapter import adapter_config
from pyams_zfiles.interfaces import IDocumentContainer, IDocumentSynchronizer
from pyams_zfiles.zmi import DocumentContainerConfigurationEditForm
from pyams_zmi.interfaces import IAdminLayer


__docformat__ = 'restructuredtext'

from pyams_zfiles import _  # pylint: disable=ungrouped-imports


@adapter_config(name='synchronizer',
                required=(IDocumentContainer, IAdminLayer,
                          DocumentContainerConfigurationEditForm),
                provides=IInnerSubForm)
class DocumentContainerSynchronizerEditForm(InnerEditForm):
    """Document container synchronizer edit form"""

    legend = _("Synchronizer configuration")

    fields = Fields(IDocumentSynchronizer)
    weight = 10
