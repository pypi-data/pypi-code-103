# Standard lib imports
import re
import sys

# Local imports
from qwilfish.constants import DEFAULT_START_SYMBOL

NONTERMINAL_REGEX_STR = r"(<[^<> ]*>)"
RE_NONTERMINAL = re.compile(NONTERMINAL_REGEX_STR)

EXP_STRING_INDEX = 0
EXP_OPTS_INDEX = 1

class GrammarError(Exception):
    '''Custom exception class for errors related to the usage of a grammar'''
    pass

def validate(grammar,
             start_symbol=DEFAULT_START_SYMBOL,
             supported_opts=None):

    if not isinstance(grammar, dict):
        return False

    if len(grammar) == 0:
        return False

    defined_nonterminals, used_nonterminals = \
        _defined_and_used_nonterminals(grammar, start_symbol)

    if defined_nonterminals is None or used_nonterminals is None:
        return False

    # Always consider the "<start>" symbol as being used
    if DEFAULT_START_SYMBOL in grammar:
        used_nonterminals.add(DEFAULT_START_SYMBOL)

    # Find undefined and unused symbols
    for unused_nonterminal in defined_nonterminals - used_nonterminals:
        print(repr(unused_nonterminal) + ": defined, but not used",
              file=sys.stderr)
    for undefined_nonterminal in used_nonterminals - defined_nonterminals:
        print(repr(undefined_nonterminal) + ": used, but not defined",
              file=sys.stderr)

    # Find unreachable symbols
    unreachable = _unreachable_nonterminals(grammar, start_symbol)
    msg_start_symbol = start_symbol
    if DEFAULT_START_SYMBOL in grammar:
        unreachable = unreachable - \
            _reachable_nonterminals(grammar, DEFAULT_START_SYMBOL)
        if start_symbol != DEFAULT_START_SYMBOL:
            msg_start_symbol += " or " + DEFAULT_START_SYMBOL
    for unreachable_nonterminal in unreachable:
        print(repr(unreachable_nonterminal) + \
              ": unreachable from " + msg_start_symbol,
              file=sys.stderr)

    # Find out what options were used and if they were supported
    used_but_not_supported_opts = set()
    if supported_opts is not None:
        used_but_not_supported_opts = opts_used(
            grammar, start_symbol).difference(supported_opts)
        for opt in used_but_not_supported_opts:
            print("warning: option " + repr(opt) + " is not supported",
                  file=sys.stderr)

    return used_nonterminals == defined_nonterminals and \
           len(unreachable) == 0

def nonterminals(expansion):
    if isinstance(expansion, tuple):
        expansion = expansion[0]

    return re.findall(RE_NONTERMINAL, expansion)

def is_nonterminal(s):
    return re.match(RE_NONTERMINAL, s)

def opts(**kwargs):
    return kwargs

def opts_used(grammar, start_symbol):
    used_opts = set()
    for symbol in grammar:
        for expansion in grammar[symbol]:
            used_opts |= set(expansion_opts(expansion).keys())
    return used_opts

def expansion_string(expansion):
    return _expansion_element(expansion, EXP_STRING_INDEX)

def expansion_opts(expansion):
    return _expansion_element(expansion, EXP_OPTS_INDEX)

def expansion_opt(expansion, attribute):
    return expansion_opts(expansion).get(attribute, None)

# Private/helper methods below

def _defined_and_used_nonterminals(grammar, start_symbol):
    defined_nonterminals = set()
    used_nonterminals = {start_symbol}

    for defined_nonterminal in grammar:
        defined_nonterminals.add(defined_nonterminal)
        expansions = grammar[defined_nonterminal]
        if not isinstance(expansions, list):
            print(repr(defined_nonterminal) + ": expansion is not a list",
                  file=sys.stderr)
            return None, None

        if len(expansions) == 0:
            print(repr(defined_nonterminal) + ": expansion list is empty",
                  file=sys.stderr)
            return None, None

        for expansion in expansions:
            if isinstance(expansion, tuple):
                expansion = expansion[0]
            if not isinstance(expansion, str):
                print(repr(defined_nonterminal) + ": " +
                      repr(expansion) + "not a string",
                      file=sys.stderr)
                return None, None

            for used_nonterminal in nonterminals(expansion):
                used_nonterminals.add(used_nonterminal)

    return defined_nonterminals, used_nonterminals

def _unreachable_nonterminals(grammar, start_symbol):
    return grammar.keys() - _reachable_nonterminals(grammar, start_symbol)

def _reachable_nonterminals(grammar, start_symbol):
    reachable = set()

    def _reachable_nonterminals_inner(grammar, symbol):
        nonlocal reachable
        reachable.add(symbol)
        for expansion in grammar.get(symbol, []):
            for nonterminal in nonterminals(expansion):
                if nonterminal not in reachable:
                    _reachable_nonterminals_inner(grammar, nonterminal)

    _reachable_nonterminals_inner(grammar, start_symbol)

    return reachable

def _expansion_element(expansion, index=EXP_STRING_INDEX):
    if isinstance(expansion, str):
        return expansion if index == EXP_STRING_INDEX else {}
    elif isinstance(expansion, tuple) and \
         len(expansion) == 2 and \
         isinstance(expansion[EXP_STRING_INDEX], str):
        return expansion[index]
    else:
        raise TypeError(repr(expansion) + \
            "Expansion is not a 2-tuple with a str in position 0")
