# -*- coding: utf-8 -*-
DST_NONE = 0x0
DST_ALL = 0x3F
DST_TRANSACTION_EVENTS = 1 << 0
DST_TRANSACTION_TRACER = 1 << 1
DST_ERROR_COLLECTOR = 1 << 2
DST_BROWSER_MONITORING = 1 << 3
DST_SPAN_EVENTS = 1 << 4
DST_TRANSACTION_SEGMENTS = 1 << 5


class AttributeFilter(object):

    def __init__(self, flattened_settings):

        self.enabled_destinations = self._set_enabled_destinations(flattened_settings)
        self.rules = self._build_rules(flattened_settings)
        self.cache = {}

    def __repr__(self):
        return "<AttributeFilter: destinations: %s, rules: %s>" % (
            bin(self.enabled_destinations), self.rules)

    @staticmethod
    def _set_enabled_destinations(settings):
        # 获得位域表示的目的地值

        enabled_destinations = DST_NONE

        if settings.get('transaction_segments.attributes.enabled', None):
            enabled_destinations |= DST_TRANSACTION_SEGMENTS

        if settings.get('span_events.attributes.enabled', None):
            enabled_destinations |= DST_SPAN_EVENTS

        if settings.get('transaction_tracer.attributes.enabled', None):
            enabled_destinations |= DST_TRANSACTION_TRACER

        if settings.get('transaction_events.attributes.enabled', None):
            enabled_destinations |= DST_TRANSACTION_EVENTS

        if settings.get('error_collector.attributes.enabled', None):
            enabled_destinations |= DST_ERROR_COLLECTOR

        if settings.get('browser_monitoring.attributes.enabled', None):
            enabled_destinations |= DST_BROWSER_MONITORING

        if not settings.get('attributes.enabled', None):
            enabled_destinations = DST_NONE

        return enabled_destinations

    @staticmethod
    def _build_rules( settings):

        rule_templates = (
            ('attributes.include', DST_ALL, True),
            ('attributes.exclude', DST_ALL, False),
            ('transaction_events.attributes.include', DST_TRANSACTION_EVENTS, True),
            ('transaction_events.attributes.exclude', DST_TRANSACTION_EVENTS, False),
            ('transaction_tracer.attributes.include', DST_TRANSACTION_TRACER, True),
            ('transaction_tracer.attributes.exclude', DST_TRANSACTION_TRACER, False),
            ('error_collector.attributes.include', DST_ERROR_COLLECTOR, True),
            ('error_collector.attributes.exclude', DST_ERROR_COLLECTOR, False),
            ('browser_monitoring.attributes.include', DST_BROWSER_MONITORING, True),
            ('browser_monitoring.attributes.exclude', DST_BROWSER_MONITORING, False),
            ('span_events.attributes.include', DST_SPAN_EVENTS, True),
            ('span_events.attributes.exclude', DST_SPAN_EVENTS, False),
            ('transaction_segments.attributes.include', DST_TRANSACTION_SEGMENTS, True),
            ('transaction_segments.attributes.exclude', DST_TRANSACTION_SEGMENTS, False),
        )

        rules = []

        for (setting_name, destination, is_include) in rule_templates:

            for setting in settings.get(setting_name) or ():
                rule = AttributeFilterRule(setting, destination, is_include)
                rules.append(rule)

        rules.sort()

        return tuple(rules)

    def apply(self, name, default_destinations):
        #  获取目的地
        if self.enabled_destinations == DST_NONE:
            return DST_NONE

        cache_index = (name, default_destinations)

        if cache_index in self.cache:
            return self.cache[cache_index]

        destinations = self.enabled_destinations & default_destinations

        for rule in self.rules:
            if rule.name_match(name):
                if rule.is_include:
                    inc_dest = rule.destinations & self.enabled_destinations
                    destinations |= inc_dest
                else:
                    destinations &= ~rule.destinations

        self.cache[cache_index] = destinations
        return destinations


class AttributeFilterRule(object):

    def __init__(self, name, destinations, is_include):
        self.name = name.rstrip('*')
        self.destinations = destinations
        self.is_include = is_include
        self.is_wildcard = name.endswith('*')  # 是否有通配符

    def _as_sortable(self):
        return self.name, not self.is_wildcard, not self.is_include

    def __eq__(self, other):
        return self._as_sortable() == other._as_sortable()

    def __ne__(self, other):
        return self._as_sortable() != other._as_sortable()

    def __lt__(self, other):
        return self._as_sortable() < other._as_sortable()

    def __le__(self, other):
        return self._as_sortable() <= other._as_sortable()

    def __gt__(self, other):
        return self._as_sortable() > other._as_sortable()

    def __ge__(self, other):
        return self._as_sortable() >= other._as_sortable()

    def __repr__(self):
        return '(%s, %s, %s, %s)' % (self.name, bin(self.destinations),
                                     self.is_wildcard, self.is_include)

    def name_match(self, name):
        if self.is_wildcard:
            return name.startswith(self.name)
        else:
            return self.name == name
