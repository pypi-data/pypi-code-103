import os

DEFAULT_TIMOUT_PAGE_LOAD = int(os.environ.get("SOP_TIMOUT_PAGE_LOAD", 3))
"""Default timeout while loading page
or moving from a menu to an other.

This default timeout for things that should
failed quickly as it should be fast as possible
and straight forward operations, loading list view
form view and so on.
"""

DEFAULT_TIMOUT_ACTION = int(os.environ.get("SOP_TIMOUT_ACTION", 5))
"""Default timeout while doing action that require
more time to compute something like generating report
genrating new invoice from sale order and loading
its form view...
"""
