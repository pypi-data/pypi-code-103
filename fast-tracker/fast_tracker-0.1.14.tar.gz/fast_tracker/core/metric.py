# -*- coding: utf-8 -*-
from collections import namedtuple

Metric = namedtuple('Metric', ['name', 'scope'])

TimeMetric = namedtuple('TimeMetric',
                        ['name', 'scope', 'duration', 'exclusive'])
