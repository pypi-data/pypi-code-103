'''
Constants used within the package
'''

DEFAULT_START_SYMBOL = "<start>"
DEFAULT_MIN_NONTERMINALS = 0
DEFAULT_MAX_NONTERMINALS = 1000

REGEX_NONTERMINAL_STR = r"(<[^<> ]*>)"

SIMPLE_GRAMMAR_EXAMPLE = {
    DEFAULT_START_SYMBOL: ["<order>"],
    "<order>": ["<greeting><order-list><goodbye>"],
    "<greeting>": ["Hello, I would like ", "Give me "],
    "<order-list>": ["<dish> and <order-list>", "<dish>."],
    "<dish>": ["a hamburger", "the pasta", "a kebab", "a pizza",
               "today's special"],
    "<goodbye>": [" Thanks!", ""]
}
