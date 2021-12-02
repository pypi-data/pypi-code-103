"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Additional functions for symbolic computing in YAML model definition
files.

"""

def IfThenElse(condition, val_if_true, val_if_false):
    """Ternary function: return either `val_if_true` or `val_if_false`
    depending on `condition`.

    """
    return val_if_true if condition else val_if_false
