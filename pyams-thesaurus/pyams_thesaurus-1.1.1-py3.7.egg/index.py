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

"""PyAMS_thesaurus.index module

"""

__docformat__ = 'restructuredtext'

from ZODB.broken import Broken
from persistent import Persistent
from zope.interface import implementer
from zope.intid import IIntIds
from zope.schema.fieldproperty import FieldProperty

from pyams_catalog.index import KeywordIndexWithInterface
from pyams_thesaurus.interfaces.index import IThesaurusTermFieldIndex, \
    IThesaurusTermsListFieldIndex
from pyams_utils.registry import query_utility


_marker = object()


def get_terms(index, term):
    """Terms getter"""
    terms = [term, ]
    if index.include_parents:
        terms.extend(term.get_parents())
    if index.include_synonyms:
        if term.usage is not None:
            terms.append(term.usage)
        else:
            terms.extend(term.used_for)
    return terms


@implementer(IThesaurusTermFieldIndex)
class ThesaurusTermFieldIndex(KeywordIndexWithInterface):
    """Thesaurus term field index"""

    include_parents = FieldProperty(IThesaurusTermFieldIndex['include_parents'])
    include_synonyms = FieldProperty(IThesaurusTermFieldIndex['include_synonyms'])

    def __init__(self, interface, discriminator, family=None,
                 include_parents=False, include_synonyms=False):
        super().__init__(interface, discriminator, family)
        self.include_parents = include_parents
        self.include_synonyms = include_synonyms

    def discriminate(self, obj, default):
        if self.interface is not None:
            obj = self.interface(obj, None)
            if obj is None:
                return default

        if callable(self.discriminator):
            value = self.discriminator(obj, _marker)
        else:
            value = getattr(obj, self.discriminator, _marker)
            if callable(value):
                value = value(obj)

        if value is _marker:
            return default

        if value:
            intids = query_utility(IIntIds)
            value = set([
                intids.register(term)
                for term in get_terms(self, value)
            ])

        if isinstance(value, Persistent):
            raise ValueError('Catalog cannot index persistent object {0!r}'.format(value))

        if isinstance(value, Broken):
            raise ValueError('Catalog cannot index broken object {0!r}'.format(value))

        return value


@implementer(IThesaurusTermsListFieldIndex)
class ThesaurusTermsListFieldIndex(KeywordIndexWithInterface):
    """Thesaurus terms list field index"""

    include_parents = FieldProperty(IThesaurusTermsListFieldIndex['include_parents'])
    include_synonyms = FieldProperty(IThesaurusTermsListFieldIndex['include_synonyms'])

    def __init__(self, interface, discriminator, family=None,
                 include_parents=False, include_synonyms=False):
        super().__init__(interface, discriminator, family)
        self.include_parents = include_parents
        self.include_synonyms = include_synonyms

    def discriminate(self, obj, default):
        if self.interface is not None:
            obj = self.interface(obj, None)
            if obj is None:
                return default

        if callable(self.discriminator):
            value = self.discriminator(obj, _marker)
        else:
            value = getattr(obj, self.discriminator, _marker)
            if callable(value):
                value = value(obj)

        if value is _marker:
            return default

        if value:
            terms = []
            for term in value:
                terms.extend(get_terms(self, term))
            if terms:
                intids = query_utility(IIntIds)
                value = set([
                    intids.register(term)
                    for term in terms
                ])
        return value
