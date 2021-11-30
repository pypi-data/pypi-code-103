#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import itertools
from osc_openapi_framework import parser


class ObjectIdentifier:
    def __init__(self):
        self._hash_to_id = dict()

    def object_id(self, field):
        name = field.name
        hash_value = hash(field)
        return self._hash_to_id[name].setdefault(
            hash_value, sorted(self._hash_to_id[name].values())[-1] + 1
        ) if name in self._hash_to_id else self._hash_to_id.setdefault(
            name, dict()).setdefault(hash_value, 0)


def walk(calls, callback):
    def step(field):
        if field.type == 'object':
            for x in field.properties.values():
                step(x)
            callback(field)
        elif field.type == 'array' and field.item.type == 'object':
            step(field.item)
    for x in calls.values():
        for y in itertools.chain(x.input_fields.values(),
                                 x.output_fields.values()):
            step(y)


def analyze(calls):
    identifier = ObjectIdentifier()
    objects = {}
    stats_by_field = {}
    stats_by_call = {}

    def actions(field):
        # mark id
        field.id = identifier.object_id(field)
        # increment stats
        stats_by_field.setdefault(field.name, list()).append(hash(field))
        stats_by_call.setdefault(field.name, dict()).setdefault(
            field.call_name, list()).append(hash(field))
        # increment object list
        objects.setdefault(hash(field), list()).append(field)
    walk(calls, actions)
    stats_by_field = [
        x for k, v in stats_by_field.items()
            for x in set(v) if len(set(v)) > 1
    ]
    stats_by_call = [
        z for x, y in stats_by_call.items()
            for k, v in y.items() for z in set(v) if len(set(v)) > 1
    ]
    return objects, stats_by_call, stats_by_field
