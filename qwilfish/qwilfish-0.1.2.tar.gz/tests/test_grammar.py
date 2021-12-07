'''
Unit tests for the main functionality of the grammar module.
'''

# Standard library imports
import unittest

# Local imports
import qwilfish.grammar as qg
from qwilfish.constants import DEFAULT_START_SYMBOL

# Grammars used for some test cases
TRIVIAL_GRAMMAR = {
    DEFAULT_START_SYMBOL : ["<phrase>"],
    "<phrase>"           : ["<hello><world>"],
    "<hello>"            : ["Hello, "],
    "<world>"            : ["world!"]
}

NONE_GRAMMAR = None

EMPTY_GRAMMAR = {}

WRONG_TYPE_GRAMMAR = ("<abc>", "def")

BAD_SYMBOL_GRAMMAR = {
    DEFAULT_START_SYMBOL : ["<illegal-symbol>"],
    "<illegal-symbol>"   : ["<<> >"],
    "<<> >"              : ["Symbol names may not contain >, < or space!"]
}

ETERNAL_GRAMMAR = {
    DEFAULT_START_SYMBOL : ["<symbol-1>"],
    "<symbol-1>"         : ["<symbol-2>"],
    "<symbol-2>"         : ["<symbol-1>"]
}

UNDEFINED_SYMBOL_GRAMMAR = {
    DEFAULT_START_SYMBOL : ["<defined-sym>"],
    "<defined-sym>"      : ["terminal", "<undefined-sym>"]
}

UNUSED_SYMBOL_GRAMMAR = {
    DEFAULT_START_SYMBOL : ["<used-sym>"],
    "<used-sym>"         : ["terminal", "another terminal"],
    "<unused-sym>"       : ["unused terminal"]
}

class TestGrammarValidate(unittest.TestCase):
    '''
    Test the validate function in the grammar module.
    '''

    def test_validate_trivial(self):
        '''
        A trivial grammar that should be valid.
        '''
        self.assertTrue(qg.validate(TRIVIAL_GRAMMAR))

    def test_validate_none(self):
        '''
        None-type objects are not valid grammars.
        '''
        self.assertFalse(qg.validate(NONE_GRAMMAR))

    def test_validate_wrong_type(self):
        '''
        Non-dict objects (in this case a tuple) are not valid grammars.
        '''
        self.assertFalse(qg.validate(WRONG_TYPE_GRAMMAR))

    def test_validate_empty(self):
        '''
        Empty dicts are not valid grammars.
        '''
        self.assertFalse(qg.validate(EMPTY_GRAMMAR))

    def test_validate_bad_symbol(self):
        '''
        Nonterminals containing >< or space make the grammar invalid.
        '''
        self.assertFalse(qg.validate(BAD_SYMBOL_GRAMMAR))

    def test_validate_eternal(self):
        '''
        Grammars that can never be completely expanded are valid (for now).
        '''
        self.assertTrue(qg.validate(ETERNAL_GRAMMAR))

    def test_validate_undefined_symbol(self):
        '''
        All nonterminals in the expansions/values must also be used as a key.
        '''
        self.assertFalse(qg.validate(UNDEFINED_SYMBOL_GRAMMAR))

    def test_validate_unused_symbol(self):
        '''
        All keys/symbols must also be used in at least one expansion/value.
        '''
        self.assertFalse(qg.validate(UNUSED_SYMBOL_GRAMMAR))



class TestGrammarNonterminals(unittest.TestCase):
    '''
    Test the nonterminals function in the grammar module.
    '''

    def test_nonterminals_basic(self):
        '''
        Find the two nonterminals in an expansion string with nothing else.
        '''
        self.assertEqual(qg.nonterminals("<a><b>"), ["<a>", "<b>"])

    def test_nonterminals_mixed(self):
        '''
        Find the two nonterminals in an expansion string with a mix of symbols.
        '''
        self.assertEqual(qg.nonterminals("<a>b<c>"), ["<a>", "<c>"])

    def test_nonterminals_bad_symbol(self):
        '''
        Don't find nonterminals with illegal names.
        '''
        self.assertEqual(qg.nonterminals("< a>"), [])

    def test_nonterminals_midst(self):
        '''
        Find a nonterminal in the midst of a string of mostly terminals.
        '''
        self.assertEqual(qg.nonterminals("abc<d>efg"), ["<d>"])

    def test_nonterminals_terminal_only(self):
        '''
        Don't find anything in a string of only terminals.
        '''
        self.assertEqual(qg.nonterminals("a b"), [])

    def test_nonterminals_annotated(self):
        '''
        Find a single annotated nonterminal symbol.
        '''
        self.assertEqual(qg.nonterminals(("<a>", {"opt": "val"})), ["<a>"])


class TestGrammarIsNonterminal(unittest.TestCase):
    '''
    Test the is_nonterminal function in the grammar module.
    '''

    def test_is_nonterminal_basic(self):
        '''
        Nonterminal symbol.
        '''
        self.assertTrue(qg.is_nonterminal("<symbol>"))

    def test_is_nonterminal_complicated_name(self):
        '''
        Nonterminal symbol with a slightly complicated name.
        '''
        self.assertTrue(qg.is_nonterminal("<complicated-symbol-123>"))

    def test_is_nonterminal_not(self):
        '''
        Terminal symbol.
        '''
        self.assertFalse(qg.is_nonterminal("terminal"))

    def test_is_nonterminal_bad_symbol_name(self):
        '''
        Nonterminal symbol with illegal name.
        '''
        self.assertFalse(qg.is_nonterminal("<<> <<> <>"))

    def test_is_nonterminal_mixed_terminal_nonterminal(self):
        '''
        Nonterminals must begin with <
        '''
        self.assertFalse(qg.is_nonterminal("a<b>"))

    def test_is_nonterminal_mixed_nonterminal_terminal(self):
        '''
        Nonterminals followed by terminals will be found
        '''
        self.assertTrue(qg.is_nonterminal("<a>b"))

    def test_is_nonterminal_missing_closing(self):
        '''
        Nonterminals must end with >
        '''
        self.assertFalse(qg.is_nonterminal("<ab"))

    def test_is_nonterminal_missing_opening(self):
        '''
        Nonterminals must begin with <
        '''
        self.assertFalse(qg.is_nonterminal("ab>"))

class TestGrammarExpansionString(unittest.TestCase):
    '''
    Test the expansion_string function in the grammar module.
    '''

    def test_is_expansion_string_empty_opts(self):
        '''
        Return symbol string in an expansion tuple with an empty dict
        '''
        symbol = "<symbol>"
        self.assertEqual(qg.expansion_string((symbol, {})), symbol)

    def test_is_expansion_string_no_opts(self):
        '''
        Return symbol string in an expansion that is not a tuple
        '''
        symbol = "<symbol>"
        self.assertEqual(qg.expansion_string(symbol), symbol)

    def test_is_expansion_string_wrong_type_int(self):
        '''
        Make sure error is raised if an int is given as the argument
        '''
        self.assertRaises(TypeError, qg.expansion_string, 7)

    def test_is_expansion_string_wrong_type_3tuple(self):
        '''
        Make sure error is raised if a 3-tuple is given as the argument
        '''
        self.assertRaises(TypeError, qg.expansion_string, ("a", {}, "b"))

    def test_is_expansion_string_wrong_type_2tuple(self):
        '''
        Make sure error is raised for 2-tuple with the wrong type in first pos
        '''
        self.assertRaises(TypeError, qg.expansion_string, (7, {}))

@unittest.skip("Expansion opts not supported yet, skipping")
class TestGrammarExpansionOpts(unittest.TestCase):
    '''
    Test the expansion_opts function in the grammar module.
    '''

    def test_is_expansion_opts_basic(self):
        '''
        An expansion that is just a string should yield an empty dict
        '''
        self.assertEqual(qg.expansion_opts("<symbol>"), {})

if __name__ == "__main__":
    unittest.main()
