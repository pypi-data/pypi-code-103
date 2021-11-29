__version__ = "0.0.1"

from hgp import model
from hgp import results

# Only print in interactive mode
import __main__ as main
if not hasattr(main, '__file__'):
    print("""Importing the gpforecaster module. L. Roque. 
    Algorithm to forecast Hierarchical Time Series providing point forecast and uncertainty intervals.\n""")
