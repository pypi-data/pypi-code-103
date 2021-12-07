# Standard lib imports
import random

# Local imports
from qwilfish.constants import DEFAULT_START_SYMBOL
from qwilfish.constants import DEFAULT_MIN_NONTERMINALS
from qwilfish.constants import DEFAULT_MAX_NONTERMINALS
from qwilfish.base_runner import BaseRunner
from qwilfish.grammar import GrammarError
from qwilfish.grammar import validate
from qwilfish.grammar import nonterminals
from qwilfish.grammar import is_nonterminal
from qwilfish.grammar import expansion_opt
from qwilfish.grammar import expansion_string
from qwilfish.derivation_tree import DerivationTreeError
from qwilfish.derivation_tree import expansion_to_children
from qwilfish.derivation_tree import all_terminals

class QwilFuzzer():

    OPT_PRE = "pre"
    OPT_POST = "post"
    OPT_PROB = "prob"
    DEFAULT_OPTS = [OPT_PRE, OPT_POST, OPT_PROB]

    def __init__(self,
                 grammar,
                 start_symbol=DEFAULT_START_SYMBOL,
                 min_nonterminals=DEFAULT_MIN_NONTERMINALS,
                 max_nonterminals=DEFAULT_MAX_NONTERMINALS,
                 supported_opts=DEFAULT_OPTS,
                 log=False):
        self.grammar = grammar
        self.start_symbol = start_symbol
        self.min_nonterminals = min_nonterminals
        self.max_nonterminals = max_nonterminals

        self.supported_opts = set()
        if supported_opts:
            for i in range(0, len(supported_opts)):
                self.supported_opts |= {supported_opts[i]}

        self.log=log
        self.check_grammar()

    def fuzz(self):
        self.derivation_tree = self.fuzz_tree()
        return all_terminals(self.derivation_tree)

    def run(self, runner=BaseRunner()):
        return runner.run(self.fuzz())

    def check_grammar(self):
        if self.start_symbol not in self.grammar:
            raise GrammarError("Start symbol" + self.start_symbol +
                               "not found in supplied grammar")
        if not validate(self.grammar, self.start_symbol,
                        self.supported_opts):
            raise GrammarError("Invalid grammar supplied")
        for nonterminal in self.grammar:
            expansions = self.grammar[nonterminal]
            _ = self.expansion_probabilities(expansions, nonterminal)

        return True

###############################################################################
############################################################### Private methods
###############################################################################

    def expand_node(self, node):
        return self.expand_node_randomly(node)

    def init_tree(self):
        return (self.start_symbol, None)

    def expansion_to_children(self, expansion):
        return expansion_to_children(expansion)

    def expand_node_min_cost(self, node):
        if self.log:
            print("Expanding", all_terminals(node), "at minimum cost")

        return self.expand_node_by_cost(node, min)

    def expand_node_max_cost(self, node):
        if self.log:
            print("Expanding", all_terminals(node), "at maximum cost")

        return self.expand_node_by_cost(node, max)

    def expand_node_randomly(self, node):
        (symbol, children) = node
        if not children is None:
            raise DerivationTreeError("Unexpandable node, children: " +
                                      children)

        if self.log:
            print("Expanding", all_terminals(node), "randomly")

        expansions = self.grammar[symbol]
        children_alternatives = \
            [self.expansion_to_children(expansion) for expansion in expansions]

        index = self.choose_node_expansion(node, children_alternatives)
        chosen_children = children_alternatives[index]

        chosen_children = self.process_chosen_children(chosen_children,
                                                       expansions[index])

        return (symbol, chosen_children)

    def opt_pre_func(self, expansion):
        return expansion_opt(expansion, QwilFuzzer.OPT_PRE)

    def opt_post_func(self, expansion):
        return expansion_opt(expansion, QwilFuzzer.OPT_POST)

    def opt_prob(self, expansion):
        return expansion_opt(expansion, QwilFuzzer.OPT_PROB)

    def process_chosen_children(self, children, expansion):
        function = self.opt_pre_func(expansion)
        if function is None:
            return children

        if not callable(function):
            raise GrammarError("Opt function 'pre' not callable")

        result = function()

        if self.log:
            print(repr(function) + "()", "=", repr(result))

        return self.apply_result(result, children)

    def apply_result(self, result, children):
        if isinstance(result, str):
            children = [(result, [])]
        elif isinstance(result, list):
            symbol_indexes = [i for i, c in enumerate(children)
                              if is_nonterminal(c[0])] # Always a tuple here

            for index, value in enumerate(result):
                if value is not None:
                    child_index = symbol_indexes[index]
                    if not isinstance(value, str):
                        value = repr(value)
                    if self.log:
                        print("Replacing", all_terminals(
                            children[child_index]), "by", value)

                    child_symbol, _ = children[child_index]
                    children[child_index] = (child_symbol, [(value, [])])
        elif isinstance(result, tuple):
            _, children = result
        elif result is None:
            pass
        elif isinstance(result, bool):
            pass
        else:
            if self.log:
                print("Replacing", "".join(
                    [all_terminals(c) for c in children]), "by", result)

            children = [(repr(result), [])]

        return children

    def choose_node_expansion(self, node, children_alternatives):
        (symbol, tree) = node
        expansions = self.grammar[symbol]
        probabilities = self.expansion_probabilities(expansions)

        weights = []
        for children in children_alternatives:
            expansion = all_terminals((symbol, children))
            children_weight = probabilities[expansion]
            if self.log:
                print(repr(expansion), "p =", children_weight)
            weights.append(children_weight)

        if sum(weights) == 0:
            return random.choices(range(len(children_alternatives)))[0]
        else:
            return random.choices(range(len(children_alternatives)),
                                  weights=weights)[0]

    def possible_expansions(self, node):
        (symbol, children) = node
        if children is None:
            return 1

        return sum(self.possible_expansions(c) for c in children)

    def any_possible_expansions(self, node):
        (symbol, children) = node
        if children is None:
            return True

        return any(self.any_possible_expansions(c) for c in children)

    def choose_tree_expansion(self, tree, children):
        return random.randrange(0, len(children))

    def expand_tree_once(self, tree):
        (symbol, children) = tree
        if children is None:
            return self.expand_node(tree)

        expandable_children = [
            c for c in children if self.any_possible_expansions(c)]

        index_map = [i for (i, c) in enumerate(children)
                     if c in expandable_children]

        child_to_be_expanded = \
            self.choose_tree_expansion(tree, expandable_children)

        children[index_map[child_to_be_expanded]] = \
            self.expand_tree_once(expandable_children[child_to_be_expanded])

        return tree

    def fuzz_tree(self):
        while True:
            tree = self.init_tree()
            tree = self.expand_tree(tree)
            symbol, children = tree
            result, new_children = self.run_post_functions(tree)
            if not isinstance(result, bool) or result:
                return (symbol, new_children)
            self.restart_expansion()

    def restart_expansion(self):
        pass

    def run_post_functions(self, tree, depth=float("inf")):
        symbol, children = tree

        if children == []:
            return True, children # Terminal symbol

        try:
            expansion = self.find_expansion(tree)
        except KeyError:
            return True, children # Expansion not found, ignore

        result = True
        function = self.opt_post_func(expansion)
        if function is not None:
            result = self.eval_function(tree, function)
            if isinstance(result, bool) and not result:
                if self.log:
                    print(all_terminals(tree),
                        "did not satisfy", symbol, "constraint")
                return False, children

            children = self.apply_result(result, children)

        if depth > 0:
            for c in children:
                result, _ = self.run_post_functions(c, depth-1)
                if isinstance(result, bool) and not result:
                    return False, children

        return result, children

    def find_expansion(self, tree):
        symbol, children = tree

        applied_expansion = \
            "".join([child_symbol for child_symbol, _ in children])

        # TODO Some intelligent mechanism to find expansions with
        # hexstring literals that have been replaced by binstrings.
        # Currently, it is not possible to have a 'post' opt if
        # hex literals are also being used in the same expression
        for expansion in self.grammar[symbol]:
            if expansion_string(expansion) == applied_expansion:
                return expansion

        raise KeyError(
            symbol +
            ": did not find expansion " +
            repr(applied_expansion))

    def eval_function(self, tree, function):
        symbol, children = tree

        if not callable(function):
            raise GrammarError("Opt function 'post' not callable")

        args = []
        for (symbol, exp) in children:
            if exp != [] and exp is not None:
                symbol_value = all_terminals((symbol, exp))
                args.append(symbol_value)

        result = function(tree, *args)
        if self.log:
            print(repr(function) + repr(tuple(args)), "=", repr(result))

        return result

    def expand_tree(self, tree):
        tree = self.expand_tree_with_strategy(
            tree, self.expand_node_max_cost, self.min_nonterminals)
        tree = self.expand_tree_with_strategy(
            tree, self.expand_node_randomly, self.max_nonterminals)
        tree = self.expand_tree_with_strategy(
            tree, self.expand_node_min_cost)

        if not self.possible_expansions(tree) == 0:
            raise DerivationTreeError("Unable to expand tree to completion")

        return tree

    def expand_tree_with_strategy(self,
                                  tree,
                                  expand_node_method,
                                  limit = None):
        self.expand_node = expand_node_method
        while ((limit is None
                or self.possible_expansions(tree) < limit)
                and self.any_possible_expansions(tree)):
            tree = self.expand_tree_once(tree)
            self.log_tree(tree)

        return tree

    def expand_node_by_cost(self, node, choose = min):
        (symbol, children) = node

        if not children is None:
            raise DerivationTreeError("Unexpandable node, children: " +
                                      children)

        expansions = self.grammar[symbol]

        children_alternatives_with_cost = [
            (self.expansion_to_children(expansion),
             self.expansion_cost(expansion, {symbol}),
             expansion)
            for expansion in expansions]

        costs = [cost for (child, cost, expansion)
                 in children_alternatives_with_cost]

        chosen_cost = choose(costs)
        children_with_chosen_cost = [child for (child, child_cost, _)
                                     in children_alternatives_with_cost
                                     if child_cost == chosen_cost]
        expansion_with_chosen_cost = [expansion for (_, child_cost, expansion)
                                      in children_alternatives_with_cost
                                      if child_cost == chosen_cost]

        index = self.choose_node_expansion(node, children_with_chosen_cost)

        chosen_children = children_with_chosen_cost[index]
        chosen_expansion = expansion_with_chosen_cost[index]
        chosen_children = self.process_chosen_children(
            chosen_children, chosen_expansion)

        return (symbol, chosen_children)

    def symbol_cost(self, symbol, seen = set()):
        expansions = self.grammar[symbol]
        return min(self.expansion_cost(e, seen | {symbol}) for e in expansions)

    def expansion_cost(self, expansion, seen = set()):
        symbols = nonterminals(expansion)

        if len(symbols) == 0:
            return 1

        if (any(s in seen for s in symbols)):
            return float("inf")

        return sum(self.symbol_cost(s, seen) for s in symbols) + 1

    def log_tree(self, tree):
        if self.log:
            print("Tree:", all_terminals(tree))

    def expansion_probabilities(self, expansions, nonterminal="<symbol>"):
        probabilities = [self.opt_prob(expansion) for expansion in expansions]
        prob_dist = self.prob_distribution(probabilities, nonterminal)

        prob_mapping = {}
        for i in range(len(expansions)):
            expansion = expansion_string(expansions[i])
            prob_mapping[expansion] = prob_dist[i]

        return prob_mapping

    def prob_distribution(self, probabilities, nonterminal="<symbol>"):
        epsilon = 0.00001

        n_unspec_probs = probabilities.count(None)
        if n_unspec_probs == 0:
            sum_probs = cast(float, sum(probabilities))
            if abs(sum_probs - 1.0) >= epsilon:
                raise GrammarError(nonterminal + \
                                   ": sum of probabilities must be 1.0")
            return probabilities

        sum_spec_probs = 0.0
        for p in probabilities:
            if p is not None:
                sum_spec_probs += p

        if sum_spec_probs < 0 or sum_spec_probs > 1.0:
           raise GrammarError(nonterminal + \
                              ": sum of probabilities must be in [0.0, 1.0]")

        default_prob = (1.0 - sum_spec_probs) / n_unspec_probs

        all_probs = []
        for p in probabilities:
            if p is None:
                p = default_prob
            all_probs.append(p)

        if abs(sum(all_probs) - 1.0) >= epsilon:
            raise GrammarError(nonterminal + \
                               ": couldn't set default probbilities")

        return all_probs
