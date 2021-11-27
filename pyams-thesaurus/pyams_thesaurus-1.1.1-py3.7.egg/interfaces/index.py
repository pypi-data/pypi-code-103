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

"""PyAMS_thesaurus.interfaces.index module

"""

from zope.interface import Interface
from zope.schema import Bool


__docformat__ = 'restructuredtext'

from pyams_thesaurus import _


class IThesaurusTermFieldIndex(Interface):
    """Thesaurus term field index interface"""

    include_parents = Bool(title=_("Include term parents into index values"),
                           default=False,
                           required=False)

    include_synonyms = Bool(title=_("Include term synonyms into index values"),
                            default=False,
                            required=False)


class IThesaurusTermsListFieldIndex(Interface):
    """Thesaurus terms list field index interface"""

    include_parents = Bool(title=_("Include term parents into index values"),
                           default=False,
                           required=False)

    include_synonyms = Bool(title=_("Include term synonyms into index values"),
                            default=False,
                            required=False)
