# -*- coding: utf-8 -*-
import os
import sys

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.join(TEST_DIR, '..')
sys.path.insert(0, PARENT_DIR)

from zwutils import logger
LOG = logger.logger(__name__, cfg='../zwtmp/conf/log.json', filesuffix='test')

if __name__ == '__main__':
    LOG.debug('xixi')
    LOG.info('haha')