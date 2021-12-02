# -*- coding: utf-8 -*-
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultKeys
from collective.transmogrifier.utils import Matcher
from Products.CMFPlone.utils import safe_unicode
from zope.interface import provider
from zope.interface import implementer
from dsgov.migration.importers.utils import Filters
from datetime import datetime

import logging


logger = logging.getLogger('Transmogrifier')


@implementer(ISection)
@provider(ISectionBlueprint)
class Importer(object):

    filter = None

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context

        if 'path-key' in options:
            pathkeys = options['path-key'].splitlines()
        else:
            pathkeys = defaultKeys(options['blueprint'], name, 'path')
        self.pathkey = Matcher(*pathkeys)

        self.filter_file = options.get('filter_file')
        self.limit = int(options.get('limit'))
        self.filter = Filters()
        self.filter.load_from_excel(self.filter_file)

    def __iter__(self):
        count = 0
        start = datetime.now()
        for item in self.previous:
            count = count + 1
            pathkey = self.pathkey(*item.keys())[0]
            logger.info('[processing item] %s: %s', count, item.get(pathkey))

            item = self.filter.update_item(item)

            yield item
            if count == self.limit:
                break
            else:
                continue

        end = datetime.now()
        passed = end - start
        logger.info('[operation time] %s', passed.__str__())
