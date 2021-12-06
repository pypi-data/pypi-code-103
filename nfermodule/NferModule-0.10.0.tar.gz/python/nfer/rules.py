from uuid import uuid4
from enum import Enum

import _nfer

# requirements:
#    1. The user should be able to add rules whenever they like
#    2. The user should be able to use rules without naming the intervals
#    3. The user should be able to refer to named intervals by name not reference
#    4. The user should be able to run Python code when an interval is matched
#    5. The user should be able to add new events or intervals manually
#    6. The user should be able to specify conditions in Python syntax
#
#    def on_interval(interval):
#        if interval.id = 50:
#            print(interval.begin)
#        print(interval.end)
#        print(interval.id)
#        rule3 = when("boo").during(interval)
#        rule3.monitor(lambda i2: print(i2.begin))
#    rule = when("foo").before("bar").where("foo.id = bar.id | foo.id = 50").map("id", "foo.id")
#    rule = when("foo").before("bar").where("foo.id == bar.id or foo.id == 50").map("id", "foo.id")
#    rule = rule.name("baz")
#    rule2 = when("baz").meet("moo").where("baz.id = moo.id").map("id", "moo.id")
#    rule2.monitor(on_interval).monitor(lambda i3: print(i3.end))
#    Nfer.monitor_all()
#    Nfer.gui(port = 8080)


class Operator(Enum):
    atomic = 0
    before = 1
    meet = 2
    during = 3
    coincide = 4
    start = 5
    finish = 6
    overlap = 7
    slice = 8
    after = 9
    follow = 10
    contain = 11


def when(interval):
    # create a new Nfer instance
    # set the lhs to the passed interval, whether it's a string or a rule
    rule = AtomicRule(interval)
    return rule

class Rule:
    def __init__(self, result, lhs, operator, rhs, conditions, data, exclusion = False):
        """Constructs a new Nfer instance"""
        self.result = result
        self.lhs = lhs
        self.rhs = rhs
        self.operator = operator
        self.conditions = conditions
        self.data = data
        self.monitored = False
        self.exclusion = exclusion

    def where(self, condition):
        # add to the conditions
        self.conditions.append(condition)
        return self

    def map(self, key, value):
        # add to the map
        self.data[key] = value
        return self

    def name(self, value):
        self.result = value
        return self

    def to_rule_syntax(self):
        lhs = self.lhs
        rhs = self.rhs
        map = []
        map_str = ""
        where = []
        where_str = ""

        if isinstance(self.lhs, Rule):
            lhs = self.lhs.result

        if isinstance(self.rhs, Rule):
            rhs = self.rhs.result

        for key, value in self.data.items():
            map.append("{} -> {}".format(key, value))

        if map:
            map_str = " map {{ {} }}".format(", ".join(map))

        for condition in self.conditions:
            where.append(condition)

        if where:
            where_str = " where {}".format(" & ".join(where))

        if self.operator == Operator.atomic:
            return "{} :- {}{}{}".format(self.result, lhs, where_str, map_str)
        elif self.exclusion:
            return "{} :- {} unless {} {}{}{}".format(self.result, lhs, self.operator.name, rhs, where_str, map_str)
        else:
            return "{} :- {} {} {}{}{}".format(self.result, lhs, self.operator.name, rhs, where_str, map_str)


class AtomicRule(Rule):
    def __init__(self, lhs):
        """Constructs a new Nfer instance"""
        super().__init__("result{}".format(str(uuid4())), lhs, Operator.atomic, None, [], {})

    def before(self, interval):
        # set to the rhs to the passed interval, whether it's a string or a rule
        return Rule(self.result, self.lhs, Operator.before, interval, self.conditions, self.data)

    def meet(self, interval):
        # set to the rhs to the passed interval, whether it's a string or a rule
        return Rule(self.result, self.lhs, Operator.meet, interval, self.conditions, self.data)

    def during(self, interval):
        # set to the rhs to the passed interval, whether it's a string or a rule
        return Rule(self.result, self.lhs, Operator.during, interval, self.conditions, self.data)

    def coincide(self, interval):
        # set to the rhs to the passed interval, whether it's a string or a rule
        return Rule(self.result, self.lhs, Operator.coincide, interval, self.conditions, self.data)

    def start(self, interval):
        # set to the rhs to the passed interval, whether it's a string or a rule
        return Rule(self.result, self.lhs, Operator.start, interval, self.conditions, self.data)

    def finish(self, interval):
        # set to the rhs to the passed interval, whether it's a string or a rule
        return Rule(self.result, self.lhs, Operator.finish, interval, self.conditions, self.data)

    def overlap(self, interval):
        # set to the rhs to the passed interval, whether it's a string or a rule
        return Rule(self.result, self.lhs, Operator.overlap, interval, self.conditions, self.data)

    def slice(self, interval):
        # set to the rhs to the passed interval, whether it's a string or a rule
        return Rule(self.result, self.lhs, Operator.slice, interval, self.conditions, self.data)
    
    def unless_after(self, interval):
        # set to the rhs to the passed interval, whether it's a string or a rule
        return Rule(self.result, self.lhs, Operator.after, interval, self.conditions, self.data, exclusion=True)
    
    def unless_follow(self, interval):
        # set to the rhs to the passed interval, whether it's a string or a rule
        return Rule(self.result, self.lhs, Operator.follow, interval, self.conditions, self.data, exclusion=True)

    def unless_contain(self, interval):
        # set to the rhs to the passed interval, whether it's a string or a rule
        return Rule(self.result, self.lhs, Operator.contain, interval, self.conditions, self.data, exclusion=True)