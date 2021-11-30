# -*- coding: utf-8 -*-
import re

from collections import namedtuple

_NormalizationRule = namedtuple('_NormalizationRule',
                                ['match_expression', 'replacement', 'ignore', 'eval_order',
                                 'terminate_chain', 'each_segment', 'replace_all'])


class NormalizationRule(_NormalizationRule):

    def __init__(self, *args, **kwargs):
        self.match_expression_re = re.compile(
            self.match_expression, re.IGNORECASE)

    def apply(self, string):
        count = 1
        if self.replace_all:
            count = 0

        return self.match_expression_re.subn(self.replacement, string, count)


class RulesEngine(object):
    # TODO 规则引擎

    def __init__(self, rules):
        self.__rules = []

        for rule in rules:
            kwargs = {}
            for name in map(str, rule.keys()):
                if name in NormalizationRule._fields:  # TODO _fields获取命名元组的字段列表
                    kwargs[name] = rule[name]
            self.__rules.append(NormalizationRule(**kwargs))

        self.__rules = sorted(self.__rules, key=lambda rule: rule.eval_order)

    @property
    def rules(self):
        return self.__rules

    def normalize(self, string):
        """
        规范化URL,对于不非法的ASCII字符串，先进行Latin-1转码
        """

        if isinstance(string, bytes):
            string = string.decode('Latin-1')

        final_string = string
        ignore = False
        for rule in self.__rules:
            if rule.each_segment:
                matched = False

                segments = final_string.split('/')
                if segments and not segments[0]:
                    rule_segments = ['']
                    segments = segments[1:]
                else:
                    rule_segments = []

                for segment in segments:
                    rule_segment, match_count = rule.apply(segment)
                    matched = matched or (match_count > 0)
                    rule_segments.append(rule_segment)

                if matched:
                    final_string = '/'.join(rule_segments)
            else:
                rule_string, match_count = rule.apply(final_string)
                matched = match_count > 0
                final_string = rule_string

            if matched:
                ignore = ignore or rule.ignore

            if matched and rule.terminate_chain:
                break
        return final_string, ignore


class SegmentCollapseEngine(object):

    COLLAPSE_STAR_RE = re.compile(r'((?:^|/)\*)(?:/\*)*')

    def __init__(self, rules):
        self.rules = {}

        prefixes = []

        for rule in rules:
            prefix_segments = rule['prefix'].rstrip('/').split('/')

            if len(prefix_segments) == 2:
                prefix = '/'.join(prefix_segments)
                self.rules[prefix] = rule['terms']
                prefixes.append(prefix)

        choices = u'|'.join([re.escape(x) for x in prefixes])
        pattern = u'^(%s)/(.+)$' % choices

        self.prefixes = re.compile(pattern)

    def normalize(self, txn_name):
        if not self.rules:
            return txn_name, False
        match = self.prefixes.match(txn_name)

        if not match:
            return txn_name, False

        prefix = match.group(1)

        whitelist_terms = self.rules.get(prefix)

        if whitelist_terms is None:
            return txn_name, False

        remainder = match.group(2)
        segments = remainder.split('/')

        result = [x if x in whitelist_terms else '*' for x in segments]
        result = self.COLLAPSE_STAR_RE.sub('\\1', '/'.join(result))

        return '/'.join((prefix, result)), False
