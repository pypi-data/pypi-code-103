# main __init__.py

__module_name__ = "__init__.py"
__author__ = ", ".join(["Michael E. Vinyard"])
__email__ = ", ".join(["vinyard@g.harvard.edu",])


from ._sequence_functions._SequenceManipulation import _SequenceManipulation as SequenceManipulator
from ._sequence_functions._SequenceGenerator import _SequenceGenerator as Seq
from ._gene_functions._GeneGenerator import _GeneGenerator as Gene
