# -*- coding: utf-8 -*-
from collections import namedtuple

TracedError = namedtuple('TracedError',
                         ['start_time', 'path', 'message', 'type', 'parameters'])
