"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Classes and functions for abstract agent management.

Part of this code is adapted from the PADAWAN framework (S. Picault,
Univ. Lille).

"""

import abc

from   sortedcontainers           import SortedSet


#  __  __      _                                 _
# |  \/  |    | |          /\                   | |
# | \  / | ___| |_ __ _   /  \   __ _  ___ _ __ | |_
# | |\/| |/ _ \ __/ _` | / /\ \ / _` |/ _ \ '_ \| __|
# | |  | |  __/ || (_| |/ ____ \ (_| |  __/ | | | |_
# |_|  |_|\___|\__\__,_/_/    \_\__, |\___|_| |_|\__|
#                                __/ |
#                               |___/

################################################################
# Metaclass for all agents
################################################################
class MetaAgent(abc.ABCMeta):
    """The Metaclass definition for all agents. When created, agents
    are stored in a class-specific dictionaries of agents. They are
    given an ID value (unique value within each class) and can be
    assigned to several agents families (by default, each agent is
    assigned to its own class).

    """
    @classmethod
    def __prepare__(mcs, name, bases, **kwds):
        families = SortedSet()
        families.add(name)
        attrs = {'agcount': 0,               # number of instances created
                 'agdict': {},               # dict of instances (ID -> agent)
                 'families': families}        # families where the class belongs
        # state NB: no need to keep information on passivity since it
        # depends on the families of the agent
        return attrs

    def __new__(mcs, name, bases, attrs, **_):
        attrs = dict(attrs)
        result = super(MetaAgent, mcs).__new__(mcs, name, bases, dict(attrs))
        result.members = tuple(attrs)
        return result
