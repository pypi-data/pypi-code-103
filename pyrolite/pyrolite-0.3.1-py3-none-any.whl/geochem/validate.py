# A set of functions for parsing, validating and formating geochemical data/metadata
import re
import functools
from .ind import (
    _common_elements,
    _common_oxides,
    common_elements,
    common_oxides,
    get_cations,
    get_isotopes
)
import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
logger = logging.getLogger(__name__)


def ischem(s):
    """
    Checks if a string corresponds to chemical component (compositional).
    Here simply checking whether it is a common element or oxide.

    Parameters
    ----------
    s : :class:`str`
        String to validate.

    Returns
    --------
    :class:`bool`

    Todo
    -----
        * Implement checking for other compounds, e.g. carbonates.
    """
    chems = set(map(str.upper, (_common_elements | _common_oxides)))
    if isinstance(s, list):
        return [str(st).upper() in chems for st in s]
    else:
        return str(s).upper() in chems


@functools.lru_cache(maxsize=None)  # cache outputs for speed
def is_isotoperatio(s):
    """
    Check if text is plausibly an isotope ratio.

    Parameters
    -----------
    s : :class:`str`
        String to validate.

    Returns
    --------
    :class:`bool`

    Todo
    -----
        * Validate the isotope masses vs natural isotopes
    """
    if s not in _common_oxides:
        isotopes = get_isotopes(s)
        return len(isotopes) == 2
    else:
        return False
