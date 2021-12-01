'''
Utilities for dealing with derivation trees represented as a tuple of
(node, children).
'''



# Standard library imports
import re

# Local imports
import qwilfish.grammar as qg

class DerivationTreeError(Exception):
    ''' Custom exception class for errors related to the derivation tree'''

def all_terminals(tree):
    '''
    Return the string tree represented by the tree thus far. Unexpanded
    nonterminals will be written as <nonterminal> in the resulting string.
    '''

    (symbol, children) = tree

    if children is None or len(children) == 0:
        return symbol

    return "".join([all_terminals(c) for c in children])

def expansion_to_children(expansion):
    '''
    Expand all symbols in an expansion string. Will return a list of
    2-tuples, one for each symbol in the expansion string. Nonterminals
    will be a tuple of the form ("<nonterminal>", None) and terminals will be
    of the form ("terminal", []).
    '''

    expansion = qg.expansion_string(expansion)

    if expansion == "": # Epsilon expansion
        return [("", [])]

    strings = re.split(qg.RE_NONTERMINAL, expansion)
    return [(s, None) if qg.is_nonterminal(s) else (s,[])
            for s in strings if len(s) > 0]
