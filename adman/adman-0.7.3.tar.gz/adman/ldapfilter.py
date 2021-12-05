import logging
from enum import IntFlag

log = logging.getLogger(__name__)

def Filter(x):
    if isinstance(x, FilterObj):
        return x
    return FilterObj(x)


MATCHING_RULE_BIT_AND = '1.2.840.113556.1.4.803'

def BitAndFilter(attr, value):
    return Filter('{}:{}:={}'.format(attr, MATCHING_RULE_BIT_AND, value))

class UserAccountControl(IntFlag):
    ACCOUNTDISABLE      = 0x00000002
    DONT_EXPIRE_PASSWD  = 0x00010000


class FilterObj:
    def __init__(self, s):
        log.debug("FilterObj.__init__(self, {!r})".format(s))
        p = s.startswith('(') + s.endswith(')')
        if p == 1:
            raise ValueError("Mismatched parenthesis")
        if p == 2:
            s = s[1:-1]
        self.s = s

    def __str__(self):
        return '(' + str(self.s) + ')'

    def __repr__(self):
        return 'FilterObj({!r})'.format(self.s)

    def __and__(self, other):
        log.debug("FilterObj.__and__({!r}, {!r})".format(self, other))
        if isinstance(other, AndGroup):
            other.members.insert(0, self)
            return other
        return AndGroup(self, other)

    def __or__(self, other):
        log.debug("FilterObj.__or__({!r}, {!r})".format(self, other))
        if isinstance(other, OrGroup):
            other.members.insert(0, self)
            return other
        return OrGroup(self, other)

    def __invert__(self):
        log.debug("FilterObj.__invert__({!r})".format(self))
        return FilterObj('(!{})'.format(self))


class FilterGroup:
    def __init__(self, operator, *members):
        log.debug("FilterGroup.__init__({!r}, {!r})".format(operator, members))
        self.operator = operator

        for m in members:
            if not isinstance(m, (FilterObj, FilterGroup)):
                raise ValueError("Argument not FilterObj or FilterGroup: {!r}".format(m))
        self.members = list(members)

    def __str__(self):
        return '(' + self.operator + ''.join(str(x) for x in self.members) + ')'

    def __repr__(self):
        return 'FilterGroup({!r}, {!r})'.format(self.operator, self.members)

    def __and__(self, other):
        log.debug("FilterGroup.__and__({!r}, {!r})".format(self, other))
        return AndGroup(self, other)

    def __or__(self, other):
        log.debug("FilterGroup.__or__({!r}, {!r})".format(self, other))
        return OrGroup(self, other)

    def __invert__(self):
        log.debug("FilterGroup.__invert__({!r})".format(self))
        # TODO: DRY with FilterObj.__invert__ ?
        return FilterObj('(!{})'.format(self))


class AndGroup(FilterGroup):
    def __init__(self, *members):
        super().__init__('&', *members)

    def __and__(self, other):
        """Special case: Combine multiple AND filters into a single group"""
        log.debug("AndGroup.__and__({!r}, {!r})".format(self, other))
        if isinstance(other, FilterObj):
            return AndGroup(*self.members, other)
        if isinstance(other, AndGroup):
            return AndGroup(*self.members, *other.members)
        raise AssertionError("unexpected type {}".format(type(other)))


class OrGroup(FilterGroup):
    def __init__(self, *members):
        super().__init__('|', *members)

    def __or__(self, other):
        """Special case: Combine multiple OR filters into a single group"""
        log.debug("OrGroup.__and__({!r}, {!r})".format(self, other))
        if isinstance(other, FilterObj):
            return OrGroup(*self.members, other)
        if isinstance(other, OrGroup):
            return OrGroup(*self.members, *other.members)
        raise AssertionError("unexpected type {}".format(type(other)))
