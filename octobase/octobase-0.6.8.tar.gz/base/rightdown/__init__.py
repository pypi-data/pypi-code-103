#!/opt/local/bin/python
# Copyright 2020, Octoboxy LLC.  All Rights Reserved.

import base


# An internal result status that's used in several parts of our processor
base.Enum.Define(('RESULT', 'Results'), (
    ('Hungry',        'hungry'),        # accepted, still need more
    ('Okay',          'okay'),          # accepted, still accepting more
    ('Halt',          'halt'),          # accepted, we are now done
    ('Full',          'full'),          # we've come to a good end, please keep your empty line
    ('OverFull',      'overfull'),      # we've come to a good end, please keep your non-empty line
    ('Broken',        'broken'),        # the lines you gave us do not match our pattern at all
))

# Couple subsets of result codes
RESULTS_OKAY_FOR_MORE   = (RESULT_HUNGRY, RESULT_OKAY)
RESULTS_ACCEPTED_CHUNK  = (RESULT_HUNGRY, RESULT_OKAY, RESULT_HALT)
RESULTS_COLLAPSE_ORDER  = (RESULT_HALT, RESULT_FULL, RESULT_OVERFULL, RESULT_OKAY)



# Inline tokens have some lookbehind/lookahead capacity, which we call position.
base.Enum.Define(('POSITION', 'Positions'), (
    ('Open',          '<'),   # expects text on the right, none on the left
    ('Close',         '>'),   # expects text on the left, none on the right
    ('Middle',        '><'),  # expects text on both sides
    ('Openish',       '--'),  # may not have text on the left
    ('Closeish',      '-'),   # may not have text on the right
    ('Selfish',       '#'),   # may not have text on either side
    ('Start',         '<<'),  # must be on the far left edge of input data
    ('End',           '>>'),  # must be on the far right edge of input data
    ('Anywhere',      ''),    # highly flexible
    ('Undefined',     None),
))



# A whole bunch of other enums are defined here
from .inlineenum  import InlineTokenTypesEnum
from .            import tokentypes
base.utils.ImportCapitalizedNamesFrom(tokentypes)


# Speculative tokenizer
from .patterns    import InitializeAllPatterns
from .tokens      import LineToken, BlockToken, InlineToken, PairedToken
from .tokenizers  import LineTokenizer, BlockTokenizer, InlineTokenizer


# Brains of the processing engine
from .processor   import Processor


# Nodes in a fully-processed document
from .nodes       import Node
from .            import blocknodes, inlinenodes
base.utils.ImportCapitalizedNamesFrom(blocknodes, inlinenodes)


# User-friendly entrypoint that abstracts away all of the above complexity
from .highlevel   import RightDownData, RightDownOptions


# Finalize the engine
InitializeAllPatterns()


# Register some unit tests
from . import tests
