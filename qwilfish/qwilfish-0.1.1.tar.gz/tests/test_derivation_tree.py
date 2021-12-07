'''
Unit tests for the main functionality of the display_tree module.
'''

# Standard library imports
import unittest

# Local imports
import qwilfish.derivation_tree as qdt

class TestDerivationTreeAllTerminals(unittest.TestCase):
    '''
    Test the all_terminals function in the display_tree module.
    '''

    def test_all_terminals_single_nonterminal(self):
        '''
        Test with a single nonterminal symbol.
        '''
        symbol = "<start>"
        tree = (symbol, None)
        self.assertEqual(qdt.all_terminals(tree), symbol)


    def test_all_terminals_single_terminal(self):
        '''
        Test with a single terminal symbol.
        '''
        symbol = "terminal"
        tree = (symbol, [])
        self.assertEqual(qdt.all_terminals(tree), symbol)

    def test_all_terminals_epsilon(self):
        '''
        Test with an epsilon expansion.
        '''
        symbol = ""
        tree = (symbol, [])
        self.assertEqual(qdt.all_terminals(tree), symbol)

    def test_all_terminals_two_level_nonterminal(self):
        '''
        Test with a two-level tree where the leaves are nonterminals.
        '''
        symbol_2a = "<symbol-2a>"
        symbol_2b = "<symbol-2b>"
        tree = ("<level-1>", [(symbol_2a, None), (symbol_2b, None)])
        expected = symbol_2a + symbol_2b
        self.assertEqual(qdt.all_terminals(tree), expected)

    def test_all_terminals_two_level_terminal(self):
        '''
        Test with a two-level tree where the leaves are terminals.
        '''
        symbol_2a = "terminal-2a"
        symbol_2b = "terminal-2b"
        tree = ("<level-1>", [(symbol_2a, []), (symbol_2b, [])])
        expected = symbol_2a + symbol_2b
        self.assertEqual(qdt.all_terminals(tree), expected)

    def test_all_terminals_two_level_mix(self):
        '''
        Test with a two-level tree with both terminals and nonterminals.
        '''
        symbol_2a = "terminal-2a"
        symbol_2b = "<nonterminal-2b>"
        symbol_2c = "terminal-2c"
        tree = ("<level-1>",
                [(symbol_2a, []), (symbol_2b, None), (symbol_2c, [])])
        expected = symbol_2a + symbol_2b + symbol_2c
        self.assertEqual(qdt.all_terminals(tree), expected)

class TestDerivationTreeExpansionToChildren(unittest.TestCase):
    '''
    Test the expansion_to_children function in the display_tree module.
    '''

    def test_expansion_to_children_single_nonterminal(self):
        '''
        Test with a single nonterminal symbol.
        '''
        self.assertEqual(qdt.expansion_to_children("<a>"),
                         [("<a>", None)])

    def test_expansion_to_children_single_terminal(self):
        '''
        Test with a single terminal symbol.
        '''
        self.assertEqual(qdt.expansion_to_children("a"),
                         [("a", [])])

    def test_expansion_to_children_list(self):
        '''
        Test with a wrongly typed expansion 2-tuple, first ele must be a str
        '''
        self.assertRaises(TypeError, qdt.expansion_to_children, ([7], []))

    def test_expansion_to_children_mix(self):
        '''
        Test with a mix of terminals and nonterminals
        '''
        self.assertEqual(qdt.expansion_to_children("<a>b<c>12"),
                         [("<a>", None), ("b", []), ("<c>", None), ("12", [])])





if __name__ == "__main__":
    unittest.main()
